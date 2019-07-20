from datetime import datetime
import requests

from django.conf import settings
from django.db import connection
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

# constants
from ..core import constants as c

# permissions
from ..core.permissions import IsDriverOrEscortUser

# models
from . import models as m
from ..account.models import User
from ..info.models import Route
from ..vehicle.models import Vehicle

# serializers
from . import serializers as s

# views
from ..core.views import TMSViewSet

# other
from ..g7.interfaces import G7Interface

from .tasks import notify_job_changes


class OrderViewSet(TMSViewSet):
    """
    Order Viewset
    """
    queryset = m.Order.objects.all()
    serializer_class = s.OrderSerializer
    # data_view_serializer_class = s.OrderDataViewSerializer

    def create(self, request):
        context = {
            'assignee': request.data.pop('assignee'),
            'customer': request.data.pop('customer'),
            'loading_station': request.data.pop('loading_station'),
            'quality_station': request.data.pop('quality_station'),
            'products': request.data.pop('products')
        }

        serializer = s.OrderSerializer(
            data=request.data, context=context
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        serializer_instance = self.get_object()

        context = {
            'assignee': request.data.pop('assignee'),
            'customer': request.data.pop('customer'),
            'loading_station': request.data.pop('loading_station'),
            'quality_station': request.data.pop('quality_station'),
            'products': request.data.pop('products')
        }

        serializer = s.OrderSerializer(
            serializer_instance,
            data=request.data,
            context=context,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def list(self, request):
        page = self.paginate_queryset(
            self.get_queryset().all()
        )

        serializer = self.serializer_class(
            page,
            many=True
        )

        return self.get_paginated_response(serializer.data)

    # @action(detail=True, url_path='jobs')
    # def get_jobs(self, request, pk=None):
    #     order = self.get_object()
    #     serializer = ShortJobSerializer(
    #         order.jobs.all(),
    #         many=True
    #     )

    #     return Response(
    #         serializer.data,
    #         status=status.HTTP_200_OK
    #     )

    @action(detail=True, url_path='vehicle-status')
    def get_vehicle_status(self, request, pk=None):
        """
        Get the vehicle status like job progress, next job client, branches
        when admin make arrangement
        """
        order = self.get_object()
        query_str = """
            select id, plate_num, total_load, branches[1] as branch1,
            branches[2] as branch2, branches[3] as branch3
            from vehicle_vehicle
        """
        with connection.cursor() as cursor:
            cursor.execute(query_str)
            columns = [col[0] for col in cursor.description]
            vehicles = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # get the current location of all registered vehicles
            body = {
                'plate_nums': [vehicle['plate_num'] for vehicle in vehicles],
                'fields': ['loc']
            }
            data = G7Interface.call_g7_http_interface(
                'BULK_VEHICLE_STATUS_INQUIRY',
                body=body
            )

            origins = []
            index = 0
            for key, value in data.items():
                if value['code'] == 0:
                    vehicles[index]['g7_error'] = False
                    origins.append(','.join([
                        str(value['data']['loc']['lng']),
                        str(value['data']['loc']['lat'])
                    ]))
                else:
                    vehicles[index]['g7_error'] = True

                index = index + 1

            # calculate the distance between new order loading and current
            destination = [
                str(order.loading_station.longitude),
                str(order.loading_station.latitude)
            ]
            queries = {
                'key': settings.MAP_WEB_SERVICE_API_KEY,
                'origins': ('|').join(origins),
                'destination': (',').join(destination)
            }
            r = requests.get(
                'https://restapi.amap.com/v3/distance', params=queries
            )
            response = r.json()
            results = response['results']
            index = 0
            for vehicle in vehicles:
                if vehicle['g7_error']:
                    vehicle['distance'] = None
                    vehicle['duration'] = None
                else:
                    vehicle['distance'] =\
                        int(results[index]['distance']) / 1000
                    vehicle['duration'] =\
                        int(results[index]['duration']) / 3600
                    index = index + 1

            serializer = s.VehicleStatusOrderSerializer(
                vehicles,
                many=True
            )
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

    @action(detail=True, methods=['post'], url_path='jobs')
    def create_or_update_job(self, request, pk=None):
        """
        Request format
        [
            {
                id: ,   // orderproductdeliver id
                arrivingDueTime: , // due time to be delivered to unloadings
                weight: ,   // product weight to be delivered to unloading
                unloading_station: {},
                job_delivers: [
                    {
                        id: ''  // jobstationproduct id [optional]
                        mission_weight: 1,
                        vehicle: { id: '', plate_nume: '' },
                        driver: { id: '', name: '' },
                        escort: { id: '', name: '' },
                        route: { id: '', name: '' },
                        loop: 1
                    }
                ]
            }
        ]
        """
        order = self.get_object()
        jobs = []
        weight_errors = {}
        job_delivers = []

        # validate weights by missions
        product = None
        product_index = -1
        unloading_station_index = 0
        for unloading_station_data in request.data:
            weight = float(unloading_station_data.get('weight', 0))
            job_delivers_data = unloading_station_data.get(
                'job_delivers', None
            )
            if job_delivers_data is None:
                raise s.serializers.ValidationError({
                    'job_delivers': 'Job deliver data is missing'
                })

            for job_deliver_data in job_delivers_data:
                orderproductdeliver = get_object_or_404(
                    m.OrderProductDeliver,
                    id=unloading_station_data.get('id', None)
                )

                job_deliver_data['orderproductdeliver'] = orderproductdeliver

                if product != orderproductdeliver.order_product.product:
                    product = orderproductdeliver.order_product.product
                    product_index = product_index + 1
                    unloading_station_index = 0

                mission_weight = float(
                    job_deliver_data.get('mission_weight', 0)
                )
                weight = weight - mission_weight

            if weight < 0:
                if product_index not in weight_errors:
                    weight_errors[product_index] = []
                weight_errors[product_index].append(unloading_station_index)
            unloading_station_index = unloading_station_index + 1
            job_delivers.extend(job_delivers_data)

        if weight_errors:
            raise s.serializers.ValidationError({
                'weight': weight_errors
            })

        # if vehicle & driver & escort is mulitple selected for delivers
        # we assume that this is one job
        for job_deliver in job_delivers:

            driver_data = job_deliver.get('driver', None)
            driver_id = driver_data.get('id', None)

            escort_data = job_deliver.get('escort', None)
            escort_id = escort_data.get('id', None)

            vehicle_data = job_deliver.get('vehicle', None)
            vehicle_id = vehicle_data.get('id', None)

            route_data = job_deliver.get('route', None)
            route_id = route_data.get('id', None)

            orderproductdeliver = job_deliver['orderproductdeliver']

            mission_weight = float(job_deliver.get('mission_weight', 0))

            for job in jobs:
                if (
                    job['driver'] == driver_id and
                    job['escort'] == escort_id and
                    job['vehicle'] == vehicle_id and
                    job['route'] == route_id
                ):

                    loading_station_products = job['stations'][0]['products']

                    for product in loading_station_products:
                        if product['product'] ==\
                           orderproductdeliver.order_product.product:
                            product['mission_weight'] += mission_weight
                            break
                    else:
                        loading_station_products.append({
                            'product':
                            orderproductdeliver.order_product.product,
                            'mission_weight': mission_weight
                        })

                    job['total_weight'] += mission_weight

                    job['stations'][0]['products'] = loading_station_products
                    job['stations'][1]['products'] = loading_station_products

                    for station in job['stations'][2:]:
                        if station['station'] ==\
                           orderproductdeliver.unloading_station:
                            station['products'].append({
                                'orderproductdeliver': orderproductdeliver,
                                'product':
                                orderproductdeliver.order_product.product,
                                'mission_weight': mission_weight
                            })
                            break
                    else:
                        job['stations'].append({
                            'station': orderproductdeliver.unloading_station,
                            'products': [{
                                'orderproductdeliver': orderproductdeliver,
                                'product':
                                orderproductdeliver.order_product.product,
                                'mission_weight': mission_weight
                            }]
                        })
                    break

            else:
                stations = []
                stations.append({
                    'station':
                    orderproductdeliver.order_product.order.loading_station,
                    'products': [{
                        'product': orderproductdeliver.order_product.product,
                        'mission_weight': mission_weight
                    }]
                })
                stations.append({
                    'station':
                    orderproductdeliver.order_product.order.quality_station,
                    'products': [{
                        'product': orderproductdeliver.order_product.product,
                        'mission_weight': mission_weight
                    }]
                })
                stations.append({
                    'station': orderproductdeliver.unloading_station,
                    'products': [{
                        'orderproductdeliver': orderproductdeliver,
                        'product': orderproductdeliver.order_product.product,
                        'mission_weight': mission_weight
                    }]
                })
                jobs.append({
                    'driver': driver_id,
                    'escort': escort_id,
                    'vehicle': vehicle_id,
                    'route': route_id,
                    'total_weight': mission_weight,
                    'stations': stations
                })

        # validate job payload;
        # 1. check if the job mission weight is over its available load
        # 2. check if the specified route is correct
        for job in jobs:
            # check if the job mission weight is over its available load
            vehicle = get_object_or_404(Vehicle, id=job['vehicle'])
            total_weight = job.get('total_weight', 0)
            if total_weight > vehicle.total_load:
                raise s.serializers.ValidationError({
                    'overweight': vehicle.plate_num
                })

            # check if the specified route is correct
            route = get_object_or_404(Route, id=job['route'])
            if route.loading_station != order.loading_station:
                raise s.serializers.ValidationError({
                    'route': 'Missing loading station'
                })

            if not order.is_same_station:
                if route.stations[1] != order.quality_station:
                    raise s.serializers.ValidationError({
                        'route': 'Missing quality station'
                    })

            for station in job['stations'][2:]:
                if station['station'] not in route.unloading_stations:
                    raise s.serializers.ValidationError({
                        'route': 'Unmatching unloading stations'
                    })

            vehicle = get_object_or_404(Vehicle, id=job['vehicle'])
            driver = get_object_or_404(User, id=job['driver'])
            escort = get_object_or_404(User, id=job['escort'])
            route = get_object_or_404(Route, id=job['route'])

            job_obj = m.Job.objects.create(
                order=order, vehicle=vehicle, driver=driver,
                escort=escort, route=route,
                total_weight=job['total_weight']
            )

            for station in job['stations']:
                job_station_obj = m.JobStation.objects.create(
                    job=job_obj,
                    station=station['station'],
                    step=route.stations.index(station['station'])
                )
                for product in station['products']:
                    m.JobStationProduct.objects.create(
                        job_station=job_station_obj,
                        product=product['product'],
                        mission_weight=product['mission_weight'],
                        orderproductdeliver=product.get(
                            'orderproductdeliver', None
                        )
                    )

            notify_job_changes.apply_async(
                args=[{
                    'job': job_obj.id
                }]
            )

        return Response(
            {'msg': 'Success'},
            status=status.HTTP_201_CREATED
        )


class OrderProductViewSet(viewsets.ModelViewSet):
    """
    OrderProduct Viewset
    """
    serializer_class = s.OrderProductSerializer

    def get_queryset(self):
        return m.OrderProduct.objects.filter(
            order_loading_station__id=self.kwargs['orderloadingstation_pk']
        )


class OrderProductDeliverViewSet(viewsets.ModelViewSet):
    """
    OrderProductDeliver ViewSet
    """
    serializer_class = s.OrderProductDeliverSerializer

    def get_queryset(self):
        return m.OrderProductDeliver.objects.filter(
            order_product__id=self.kwargs['orderproduct_pk']
        )


class JobViewSet(TMSViewSet):

    queryset = m.Job.objects.all()
    serializer_class = s.JobSerializer

    @action(detail=False, url_path='vehicles')
    def get_vehicle_jobs_by_time(self, request):
        """
        Query the job list depending on vehicle plate number and time
        This api endpoint is used in playback in frontend
        """
        plate_num = request.query_params.get('plate_num', None)
        from_date = request.query_params.get('from', None)
        to_date = request.query_params.get('to', None)

        if plate_num is None or from_date is None or to_date is None:
            return Response(
                {
                    'result': {
                        'code': '1',
                        'msg': 'Improperly configured parameters'
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        # jobs = m.Job.objects.filter(
        #     Q(vehicle__plate_num=plate_num) & Q(started_on__gte=from_date) &
        #     (Q(finished_on__lte=to_date) | Q(finished_on=None))
        # ).order_by('started_on')

        jobs = m.Job.objects.filter(
            Q(vehicle__plate_num=plate_num) & Q(started_on__gte=from_date) &
            Q(finished_on__lte=to_date)
        ).order_by('started_on')

        serializer = s.JobByVehicleSerializer(
            jobs, many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, url_path='playback')
    def get_vehicle_playback_by_job(self, request, pk=None):
        job = self.get_object()

        queries = {
            'plate_num': job.vehicle.plate_num,
            'from': job.started_on.strftime('%Y-%m-%d %H:%M:%S'),
            'to': job.finished_on.strftime('%Y-%m-%d %H:%M:%S'),
            'timeInterval': 10
        }

        try:
            data = G7Interface.call_g7_http_interface(
                'VEHICLE_HISTORY_TRACK_QUERY',
                queries=queries
            )
            if data is None:
                results = []
            else:
                paths = []

                index = 0
                for x in data:
                    paths.append([x.pop('lng'), x.pop('lat')])
                    x['no'] = index
                    x['time'] = datetime.utcfromtimestamp(
                        int(x['time'])/1000
                    ).strftime('%Y-%m-%d %H:%M:%S')
                    index = index + 1

                results = {
                    'paths': paths,
                    'meta': data
                }

            return Response(
                results,
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {
                    'result': {
                        'code': '1',
                        'msg': 'g7 error'
                    }
                }
            )

    @action(
        detail=False, url_path='mileage'
    )
    def get_mileage(self, request):
        page = self.paginate_queryset(
            m.Job.objects.all()
        )

        serializer = s.JobMileageSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    @action(
        detail=False, url_path='documents'
    )
    def get_documents(self, request):
        page = self.paginate_queryset(
            m.Job.objects.all()
        )
        serializer = s.JobDocumentSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False, url_path='time'
    )
    def get_time(self, request):
        page = self.paginate_queryset(
            m.Job.objects.all(),
        )

        serializer = s.JobTimeDurationSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    @action(
        detail=False, url_path='driving'
    )
    def get_driving(self, request):
        pass

    @action(
        detail=False, url_path='previous',
        permission_classes=[IsDriverOrEscortUser]
    )
    def previous_jobs(self, request):
        serializer = s.JobDoneSerializer(
            request.user.jobs_as_driver.filter(
                finished_on__lte=timezone.now()
            ),
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(
        detail=False, url_path='done',
        permission_classes=[IsDriverOrEscortUser]
    )
    def done_jobs(self, request):
        page = self.paginate_queryset(
            request.user.jobs_as_driver.filter(
                progress=c.JOB_PROGRESS_COMPLETE
            ).order_by('-finished_on')
        )

        serializer = s.JobDoneSerializer(
            page,
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False, url_path='current',
        permission_classes=[IsDriverOrEscortUser]
    )
    def progress_jobs(self, request):
        job = request.user.jobs_as_driver.filter(
            ~(Q(progress=c.JOB_PROGRESS_NOT_STARTED) |
                Q(progress=c.JOB_PROGRESS_COMPLETE))
        ).first()

        # if job is None:
        #     job = request.user.driver_profile.jobs.filter(
        #         progress=c.JOB_PROGRESS_NOT_STARTED
        #     ).first()

        if job is not None:
            ret = s.JobCurrentSerializer(job).data
        else:
            ret = {}

        return Response(
            ret,
            status=status.HTTP_200_OK
        )

    @action(
        detail=False, url_path='future',
        permission_classes=[IsDriverOrEscortUser]
    )
    def future_jobs(self, request):
        page = self.paginate_queryset(
            request.user.jobs_as_driver.filter(
                progress=c.JOB_PROGRESS_NOT_STARTED
            )
        )

        serializer = s.JobCurrentSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True, url_path='update-progress',
        permission_classes=[IsDriverOrEscortUser]
    )
    def progress_update(self, request, pk=None):
        job = self.get_object()

        current_progress = job.progress
        if current_progress == c.JOB_PROGRESS_COMPLETE:
            return Response(
                {
                    'progress': 'This is already completed progress',
                    'last_progress_finished_on': job.finished_on
                },
                status=status.HTTP_200_OK
            )

        if current_progress == c.JOB_PROGRESS_NOT_STARTED:
            job.started_on = timezone.now()
            last_progress_finished_on = None
        else:
            current_station = job.jobstation_set.filter(
                is_completed=False
            ).first()

            sub_progress =\
                (current_progress - c.JOB_PROGRESS_TO_LOADING_STATION) % 4
            if sub_progress == 0:
                current_station.arrived_station_on = timezone.now()
                current_station.save()
                if current_station.step == 0:
                    last_progress_finished_on = job.started_on
                else:
                    last_progress_finished_on =\
                        current_station.previous_station.departure_station_on
            elif sub_progress == 1:
                current_station.started_working_on = timezone.now()
                last_progress_finished_on = current_station.arrived_station_on
                current_station.save()
            elif sub_progress == 2:
                current_station.finished_working_on = timezone.now()
                last_progress_finished_on = current_station.started_working_on
                current_station.save()
            elif sub_progress == 3:
                current_station.departure_station_on = timezone.now()
                last_progress_finished_on = current_station.finished_working_on
                current_station.is_completed = True
                current_station.save()

                if not current_station.has_next_station:
                    job.progress = c.JOB_PROGRESS_COMPLETE
                    job.finished_on = timezone.now()

                    # update job empty mileage
                    loading_station_arrived_on =\
                        job.jobstation_set.get(step=0).arrived_station_on

                    queries = {
                        'plate_num':
                            job.vehicle.plate_num,
                        'from':
                            job.started_on.strftime('%Y-%m-%d %H:%M:%S'),
                        'to':
                            loading_station_arrived_on.strftime(
                                '%Y-%m-%d %H:%M:%S'
                            )
                    }
                    data = G7Interface.call_g7_http_interface(
                        'VEHICLE_GPS_TOTAL_MILEAGE_INQUIRY',
                        queries=queries
                    )
                    job.empty_mileage = data['total_mileage']

                    # update job heavy mileage
                    queries = {
                        'plate_num':
                            job.vehicle.plate_num,
                        'from':
                            loading_station_arrived_on.strftime(
                                '%Y-%m-%d %H:%M:%S'
                            ),
                        'to':
                            job.finished_on.strftime(
                                '%Y-%m-%d %H:%M:%S'
                            )
                    }
                    job.heavy_mileage = data['total_mileage']
                    job.total_mileage =\
                        job.empty_mileage + job.heavy_mileage
                    job.highway_mileage = 0
                    job.normalway_mileage = 0
                    job.save()
                    return Response(
                        {
                            'progress': c.JOB_PROGRESS_COMPLETE,
                            'last_progress_finished_on':
                            last_progress_finished_on
                        },
                        status=status.HTTP_200_OK
                    )
        job.progress = current_progress + 1
        job.save()

        return Response(
            {
                'progress': job.progress,
                'last_progress_finished_on': last_progress_finished_on,
            },
            status=status.HTTP_200_OK
        )

    @action(
        detail=True, url_path='upload-bill-document', methods=['post']
    )
    def upload_bill_document(self, request, pk=None):
        job = self.get_object()
        serializer = s.JobBillSerializer(
            data=request.data,
            context={
                'request': request
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        job.bills.add(serializer.instance)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(
        detail=True, url_path='documents'
    )
    def get_job_documents(self, request, pk=None):
        job = self.get_object()
        documents = {}

        for bill in job.bills.all():
            category = bill.category

            if category not in documents:
                documents[category] = []

            documents[category].append(
                s.JobBillViewSerializer({
                    'amount': bill.amount,
                    'unit_price': bill.unit_price,
                    'cost': bill.cost,
                    'document': bill.document
                }, context={'request': request}).data
            )

        for job_station in job.jobstation_set.all():
            documents[job_station.station.station_type] = []
            for job_product in job_station.jobstationproduct_set.all():
                documents[job_station.station.station_type].append(
                    s.JobBillViewSerializer({
                        'document': job_product.document,
                        'weight': job_product.weight
                    }, context={'request': request}).data
                )

        return Response(
            documents,
            status=status.HTTP_200_OK
        )

    @action(
        detail=False, url_path="bill-documents"
    )
    def get_bills(self, request):
        """
        for driver app
        return bills
        """
        bill_type = request.query_params.get('type', 'all')
        page = self.paginate_queryset(
            request.user.jobs_as_driver.filter(
                ~Q(progress=c.JOB_PROGRESS_NOT_STARTED)
            )
        )

        serializer = s.JobBillDocumentForDriverSerializer(
            page,
            context={'request': request, 'bill_type': bill_type},
            many=True
        )
        return self.get_paginated_response(serializer.data)


class JobStationViewSet(viewsets.ModelViewSet):

    serializer_class = s.JobStationSerializer

    def get_queryset(self):
        return m.JobStation.objects.filter(
            job__id=self.kwargs['job_pk']
        )


class JobStationProductViewSet(viewsets.ModelViewSet):

    serializer_class = s.JobStationProductSerializer

    def get_queryset(self):
        return m.JobStationProduct.objects.filter(
            job_station__id=self.kwargs['job_station_pk']
        )

    @action(
        detail=True, url_path='upload-product-document', methods=['post']
    )
    def upload_product_document(self, request, job_pk=None,
                                job_station_pk=None, pk=None):
        """
        for driver app;
        driver shoud upload the product document in each station
        this api end point is used to upload the product document weight
        weight is different from mission weight
        """
        instance = self.get_object()
        serializer = s.JobStationProductDocumentSerializer(
            instance,
            data=request.data,
            context={'request': request},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class JobReportViewSet(viewsets.ModelViewSet):

    queryset = m.JobReport.objects.all()
    serializer_class = s.DriverJobReportSerializer

    @action(detail=False, url_path='me')
    def me(self, request):
        page = self.paginate_queryset(
            request.user.report.all()
        )
        serializer = s.JobReportSEr(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

        return Response(
            request.user.report.all()
        )
        return request.user
