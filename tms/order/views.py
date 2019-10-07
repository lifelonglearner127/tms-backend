from datetime import datetime, timedelta
from pytz import timezone as tz
import requests

from django.conf import settings
from django.db import connection
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.generics import DestroyAPIView
from rest_framework.decorators import action
from rest_framework.response import Response

# constants
from ..core import constants as c

# permissions
from ..core.permissions import (
    IsDriverOrEscortUser, IsCustomerUser, OrderPermission
)

# models
from . import models as m
from ..account.models import User
from ..info.models import Station, Product
from ..route.models import Route
from ..vehicle.models import Vehicle

# serializers
from . import serializers as s
from ..vehicle.serializers import VehiclePositionSerializer

# views
from ..core.views import TMSViewSet

# other
from ..g7.interfaces import G7Interface


class OrderCartViewSet(TMSViewSet):

    queryset = m.OrderCart.objects.all()
    serializer_class = s.OrderCartSerializer
    permission_classes = [IsCustomerUser]

    def create(self, request):
        context = {
            'product': request.data.pop('product'),
            'customer': request.user.customer_profile
        }

        serializer = self.serializer_class(
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
            'product': request.data.pop('product')
        }

        serializer = self.serializer_class(
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


class OrderViewSet(TMSViewSet):
    """
    Order Viewset
    """
    queryset = m.Order.objects.all()
    serializer_class = s.OrderSerializer
    permission_classes = [OrderPermission]

    def create(self, request):

        context = {
            'products': request.data.pop('products'),
            'loading_station': request.data.pop('loading_station'),
            'quality_station': request.data.pop('quality_station')
        }
        data = request.data
        if request.user.user_type == c.USER_TYPE_CUSTOMER:
            data['customer'] = {
                'id': request.user.customer_profile.id
            }
            data['order_source'] = c.ORDER_SOURCE_CUSTOMER
        else:
            data['order_source'] = c.ORDER_SOURCE_INTERNAL

        serializer = s.OrderSerializer(
            data=data, context=context
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        serializer_instance = self.get_object()
        if serializer_instance.status == c.ORDER_STATUS_COMPLETE:
            return Response(
                {
                    'msg': 'Already finished'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data
        context = {
            'products': request.data.pop('products'),
            'loading_station': request.data.pop('loading_station'),
            'quality_station': request.data.pop('quality_station')
        }
        if request.user.user_type == c.USER_TYPE_CUSTOMER:
            data['customer'] = {
                'id': request.user.customer_profile.id
            }
            data['order_source'] = c.ORDER_SOURCE_CUSTOMER
        else:
            data['order_source'] = c.ORDER_SOURCE_INTERNAL

        serializer = s.OrderSerializer(
            serializer_instance,
            data=data,
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

    @action(detail=True, url_path='job', methods=['post'])
    def create_job(self, request, pk=None):
        """
        payload:
        {
            vehicle: {},
            driver: {},
            escort: {},
            routes: {},
            loop: {}
            branches: [
                {
                    branch: {},
                    product: {},
                    missionWeight: {},
                    unloadingStations: {
                        unloadingStation: {},
                        dueTime: {},
                        missionWeight
                    }
                }
            ]
        }
        """
        order = self.get_object()
        if order.status == c.ORDER_STATUS_COMPLETE:
            return Response(
                {
                    'msg': 'Already finished'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # validate vehicle
        try:
            vehicle = Vehicle.objects.get(
                id=request.data.pop('vehicle', None)
            )
        except Vehicle.DoesNotExist:
            raise s.serializers.ValidationError({
                'vehicle': 'Such vehicle does not exist'
            })

        # validate driver
        try:
            driver = User.objects.get(
                id=request.data.pop('driver', None)
            )
        except User.DoesNotExist:
            raise s.serializers.ValidationError({
                'driver': 'Such driver does not exist'
            })

        # validate escort
        try:
            escort = User.objects.get(
                id=request.data.pop('escort', None)
            )
        except User.DoesNotExist:
            raise s.serializers.ValidationError({
                'escort': 'Such escort does not exist'
            })

        # check if branch weight exceed vehicle branch weight
        errors = {}
        branches_data = request.data.pop('branches', [])
        job_products = {
            'total': []
        }
        for branch_data in branches_data:
            branch = branch_data.get('branch', 0)
            product = branch_data.get('product')
            branch_weight = float(branch_data.get('mission_weight', 0))

            # restructure by job station such data structure
            # {
            #     'total': [
            #         {
            #             'product': id,
            #             'branch': id,
            #             'mission_weight': 0
            #         }
            #     ],
            #     'station_id': [
            #         {
            #             'product': id,
            #             'branch': id,
            #             'due_time': {},
            #             'mission_weight': 0,
            #         }
            #     ]
            # }
            # restructure by job station
            job_products['total'].append({
                'product': product,
                'branch': branch,
                'mission_weight': branch_weight
            })

            if vehicle.branches[branch] < float(branch_data.get('mission_weight')):
                if branch not in errors:
                    errors[branch] = {}
                errors[branch]['branch_over_weight'] = 'mission weight exceed vehicle branch actual load'

            for unloading_station_data in branch_data.get('unloading_stations', []):
                unloading_station_id = unloading_station_data.get('unloading_station')
                due_time = unloading_station_data.get('due_time')
                unloading_station_weight = float(unloading_station_data.get('mission_weight', 0))
                branch_weight = branch_weight - unloading_station_weight

                # restructure by job station
                if unloading_station_id not in job_products:
                    job_products[unloading_station_id] = []

                job_products[unloading_station_id].append({
                    'product': product,
                    'branch': branch,
                    'due_time': due_time,
                    'mission_weight': unloading_station_weight
                })

            if branch_weight != 0:
                if branch not in errors:
                    errors[branch] = {}
                errors[branch]['station_over_weight'] =\
                    'sum of unloading weights does not match with branch mission weight'

        if errors:
            return Response(
                errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        # validate if arrange weight exceed order product weight
        arranged_products = {}
        # {
        #     'product_id': {
        #         'branch': [],
        #         'mission_weight': 0
        #     }
        # }
        for job_product in job_products['total']:
            product_id = job_product['product']
            if product_id not in arranged_products:
                arranged_products[product_id] = {
                    'branch': [job_product['branch']],
                    'mission_weight': job_product['mission_weight']
                }
            else:
                arranged_products[product_id]['mission_weight'] += job_product['mission_weight']
                arranged_products[product_id]['branch'].append(job_product['branch'])

        for product_id, arranged_product in arranged_products.items():
            order_product = get_object_or_404(m.OrderProduct, order=order, product__id=product_id)
            if order_product.weight - order_product.arranged_weight < arranged_product['mission_weight']:
                for arranged_branch in arranged_product['branch']:
                    if arranged_branch not in errors:
                        errors[arranged_branch] = {}
                        errors[arranged_branch]['order_over_weight'] = 'mission weight exceed order weight'

        if errors:
            return Response(
                errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        route_ids = request.data.pop('routes', [])
        routes = Route.objects.filter(id__in=route_ids)
        routes = dict([(route.id, route) for route in routes])
        routes = [routes[id] for id in route_ids]

        # route validations
        if not order.is_same_station:
            routes = routes[1:]

        if len(routes) != len(job_products.keys()) - 1:
            if 'routes' not in errors:
                errors['routes'] = 'Route and station does not match'

        if errors:
            return Response(
                errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        for key in job_products.keys():
            if key == 'total':
                continue

            for route in routes:
                if key == route.end_point.id:
                    break
            else:
                if 'routes' not in errors:
                    errors['routes'] = []
                errors['routes'].append(key)

        if errors:
            return Response(
                errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        # create job & associated driver and escort instance
        job = m.Job.objects.create(order=order, vehicle=vehicle, routes=route_ids)
        m.JobDriver.objects.create(job=job, driver=driver)
        m.JobEscort.objects.create(job=job, escort=escort)

        job_loading_station = m.JobStation.objects.create(
            job=job, station=order.loading_station, step=0
        )
        job_quality_station = m.JobStation.objects.create(
            job=job, station=order.quality_station, step=1
        )

        for product_id, arranged_product in arranged_products.items():
            order_product = get_object_or_404(m.OrderProduct, order=order, product__id=product_id)
            order_product.arranged_weight += arranged_product['mission_weight']
            order_product.save()

        for job_product in job_products['total']:
            m.JobStationProduct.objects.create(
                job_station=job_loading_station,
                product=get_object_or_404(Product, id=job_product['product']),
                branch=job_product['branch'],
                mission_weight=job_product['mission_weight']
            )
            m.JobStationProduct.objects.create(
                job_station=job_quality_station,
                product=get_object_or_404(Product, id=job_product['product']),
                branch=job_product['branch'],
                mission_weight=job_product['mission_weight']
            )

        for route_index, route in enumerate(routes):
            job_station = m.JobStation.objects.create(
                job=job, station=route.end_point, step=route_index+2
            )
            for job_product in job_products[route.end_point.id]:
                m.JobStationProduct.objects.create(
                    job_station=job_station,
                    product=get_object_or_404(Product, id=job_product['product']),
                    branch=job_product['branch'],
                    due_time=job_product['due_time'],
                    mission_weight=job_product['mission_weight']
                )

        return Response(
            s.JobAdminSerializer(job).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, url_path='jobs')
    def get_jobs(self, request, pk=None):
        order = self.get_object()
        serializer = s.JobAdminSerializer(
            order.jobs.all(),
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

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
            try:
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
                    # calculate the distance between new order loading
                    # and current position
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
            except Exception:
                for vehicle in vehicles:
                    vehicle['g7_error'] = True
                    vehicle['distance'] = None
                    vehicle['duration'] = None

            serializer = s.VehicleStatusOrderSerializer(
                vehicles,
                many=True
            )
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

    @action(
        detail=False, methods=['get'], url_path='me',
        permission_classes=[IsCustomerUser]
    )
    def get_customer_orders(self, request):
        queryset = m.Order.objects.filter(
            customer=request.user.customer_profile
        )

        order_status = request.query_params.get('status', None)
        if order_status == c.ORDER_STATUS_PENDING:
            queryset = queryset.filter(status=order_status)
        elif order_status == c.ORDER_STATUS_INPROGRESS:
            queryset = queryset.filter(status=order_status)
        elif order_status == c.ORDER_STATUS_COMPLETE:
            queryset = queryset.filter(status=order_status)

        page = self.paginate_queryset(queryset)

        serializer = s.OrderCustomerAppSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    @action(detail=True, url_path='position')
    def get_all_vehicle_positions(self, request, pk=None):
        """
        Get the current location of all in-progress order-job vehicles
        This api will be called at most once when customer click monitoring
        After then vehicle positioning data will be notified via web sockets
        """
        order = self.get_object()
        if order.status == c.ORDER_STATUS_COMPLETE:
            return Response(
                {'order': 'This order is already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if order.status == c.ORDER_STATUS_PENDING:
            return Response(
                {'order': 'This order is still in pending'},
                status=status.HTTP_400_BAD_REQUEST
            )

        plate_nums = order.jobs.filter(progress__gt=1).values_list(
            'vehicle__plate_num', flat=True
        )
        if len(plate_nums) == 0:
            return Response(
                {'job': 'Not job started'},
                status=status.HTTP_400_BAD_REQUEST
            )
        body = {
            'plate_nums': list(plate_nums),
            'fields': ['loc']
        }
        data = G7Interface.call_g7_http_interface(
            'BULK_VEHICLE_STATUS_INQUIRY',
            body=body
        )
        ret = []
        for key, value in data.items():
            if value['code'] == 0:
                ret.append(value)

        serializer = VehiclePositionSerializer(
            ret, many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
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


class JobViewSet(TMSViewSet):

    queryset = m.Job.objects.all()
    serializer_class = s.JobSerializer

    def create(self, request):
        """
        This api is called when staff member create the jobs for order
        """
        order = get_object_or_404(m.Order, id=request.data.pop('order', None))

        # cannot create a job for completed order
        if order.status == c.ORDER_STATUS_COMPLETE:
            return Response(
                {
                    'msg': 'Already finished'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # load ordered projects with not-delivered weight
        order_products = []
        for order_product in order.orderproduct_set.all():
            order_products.append({
                'product': order_product.product,
                'left_weight': order_product.weight - order_product.delivered_weight
            })

        # check if the payload is empty or not
        jobs_data = request.data.pop('jobs', [])
        if not len(jobs_data):
            return Response(
                {'data': 'No data is provied'},
                status=status.HTTP_200_OK
            )

        # validation check, weight validation, route validation
        errors = {}
        job_index = 0

        for job_data in jobs_data:
            job_data['total_weight'] = 0

            vehicle_data = job_data.get('vehicle', None)
            if vehicle_data is None:
                if job_index not in errors:
                    errors[job_index] = {}
                errors[job_index]['vehicle'] = 'Missing data'

            job_data['vehicle'] = get_object_or_404(
                Vehicle, id=vehicle_data.get('id', None)
            )

            driver_data = job_data.get('driver', None)
            if driver_data is None:
                if job_index not in errors:
                    errors[job_index] = {}
                errors[job_index]['driver'] = 'Missing data'

            job_data['driver'] = get_object_or_404(
                User, id=driver_data.get('id', None), user_type=c.USER_TYPE_DRIVER
            )

            escort_data = job_data.get('escort', None)
            if escort_data is None:
                if job_index not in errors:
                    errors[job_index] = {}
                errors[job_index]['escort'] = 'Missing data'

            job_data['escort'] = get_object_or_404(
                User, id=escort_data.get('id', None), user_type=c.USER_TYPE_ESCORT
            )

            branch_index = 0
            job_data['stations'] = []
            job_data['stations'].append({
                'station': order.loading_station,
                'products': []
            })
            job_data['stations'].append({
                'station': order.quality_station,
                'products': []
            })

            for branch_data in job_data['branches']:
                branch_id = int(branch_data.get('branch').get('id'))
                branch_mission_weight = float(
                    branch_data.get('mission_weight')
                )

                job_data['total_weight'] += branch_mission_weight

                # check if the branch mission weight exceed vehicle branch load
                if job_data['vehicle'].branches[branch_id] < float(branch_data.get('mission_weight')):
                    if job_index not in errors:
                        errors[job_index] = {}

                    if branch_id not in errors[job_index]:
                        errors[job_index][branch_index] = {}

                    errors[job_index][branch_index]['branch_over_weight'] =\
                        'mission weight exceed vehicle branch actual load'

                product_data = branch_data.pop('product', None)
                product = get_object_or_404(
                    Product, id=product_data.get('id', None)
                )

                for order_product in order_products:
                    if order_product['product'] == product:
                        order_product['left_weight'] -= branch_mission_weight

                for i in range(0, 2):
                    job_data['stations'][i]['products'].append({
                        'product': product,
                        'branch': branch_id,
                        'mission_weight': branch_mission_weight
                    })

                unloading_stations_data = branch_data.pop('unloading_stations')

                for unloading_station_data in unloading_stations_data:
                    station_data = unloading_station_data.get(
                        'unloading_station'
                    )
                    station = get_object_or_404(
                        Station, id=station_data.get('id', None)
                    )

                    if station not in job_data['route'].unloading_stations:
                        if job_index not in errors:
                            errors[job_index] = {}
                        if 'route' not in errors[job_index]:
                            errors[job_index]['route'] = []
                        errors[job_index]['route'].append('unloading')

                    due_time = unloading_station_data.get(
                        'due_time'
                    )
                    unloading_station_mission_weight = float(unloading_station_data.get('mission_weight', 0))
                    branch_mission_weight -= unloading_station_mission_weight
                    for unloading_station in job_data['stations'][2:]:
                        if unloading_station['station'] == station:
                            unloading_station['products'].append({
                                'product': product,
                                'branch': branch_id,
                                'mission_weight': unloading_station_mission_weight
                            })
                            break

                    else:
                        job_data['stations'].append({
                            'station': station,
                            'due_time': due_time,
                            'products': [{
                                'product': product,
                                'branch': branch_id,
                                'mission_weight': unloading_station_mission_weight
                            }]
                        })

                if branch_mission_weight != 0:
                    if job_index not in errors:
                        errors[job_index] = {}
                    if branch_index not in errors[job_index]:
                        errors[job_index][branch_index] = {}

                    errors[job_index][branch_index]['station_over_weight'] =\
                        'sum of unloading weights overweight branch missin weight'

                branch_index += 1

            job_index += 1

        product_index = 0
        for order_product in order_products:
            if order_product['left_weight'] < 0:
                if 'order' not in errors:
                    errors['order'] = {}
                errors['order'][product_index] = 'arrange weight exceed order weight'

        if errors:
            return Response(
                errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        for job_data in jobs_data:
            job = m.Job.objects.create(
                order=order,
                vehicle=job_data['vehicle'],
                total_weight=job_data['total_weight']
            )

            station_index = 0
            for station in job_data['stations']:
                if station_index < 2:
                    step = station_index
                    station_index += 1
                else:
                    step = job_data['route'].stations.index(station['station'])
                    if job_data['is_same_station']:
                        step += 1

                job_station = m.JobStation.objects.create(
                   job=job,
                   station=station['station'],
                   step=step,
                   due_time=station['due_time']
                )

                for job_station_product in station['products']:
                    m.JobStationProduct.objects.create(
                        job_station=job_station,
                        **job_station_product
                    )

        if jobs_data is not None:
            order.arrangement_status = c.TRUCK_ARRANGEMENT_STATUS_INPROGRESS
            order.save()

        return Response(
            {'msg': 'Ok'},
            status=status.HTTP_200_OK
        )

    def retrieve(self, request, pk=None):
        pass

    def update(self, request, pk=None):
        pass

    @action(detail=True, methods=['post'], url_path='upload-loading-check')
    def upload_loading_station_check(self, request, pk=None):
        job = self.get_object()
        images = request.data.pop('images')
        product = get_object_or_404(Product, id=request.data.get('product').get('id'))

        loading_check, created = m.LoadingStationProductCheck.objects.get_or_create(
            job=job, product=product
        )

        loading_check.weight = request.data.pop('weight')
        loading_check.save()

        loading_check.images.all().delete()

        for image in images:
            image['loading_station'] = loading_check.id
            serializer = s.LoadingStationDocumentSerializer(data=image)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response(s.LoadingStationProductCheckSerializer(loading_check).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='upload-quality-check')
    def upload_quality_check(self, request, pk=None):
        job = self.get_object()
        images = request.data.pop('images')
        branch = request.data.get('branch', 0)

        quality_check, created = m.QualityCheck.objects.get_or_create(
            job=job, branch=branch
        )
        quality_check.density = request.data.pop('density')
        quality_check.additive = request.data.pop('additive')
        quality_check.save()

        job_qualitystation = job.jobstation_set.all()[1]

        job_qualitystation_product = get_object_or_404(
            m.JobStationProduct, job_station=job_qualitystation, branch=branch
        )
        job_qualitystation_product.volume = request.data.pop('volume')
        job_qualitystation_product.man_hole = request.data.pop('man_hole')
        job_qualitystation_product.branch_hole = request.data.pop('branch_hole')

        for image in images:
            image['job_station_product'] = job_qualitystation_product.id
            serializer = s.JobStationProductDocumentSerializer(data=image)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response(
            {'msg': 'Successfully uploaded'},
            status=status.HTTP_200_OK
        )

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

        start_time = timezone.localtime(job.started_on).strftime(
            '%Y-%m-%d %H:%M:%S'
        )
        finish_time = timezone.localtime(job.finished_on).strftime(
            '%Y-%m-%d %H:%M:%S'
        )
        results = {
            'total_distance': 0,
            'paths': [],
            'meta': []
        }
        while True:
            queries = {
                'plate_num': job.vehicle.plate_num,
                'from': start_time,
                'to': finish_time,
                'timeInterval': '10'
            }
            try:
                data = G7Interface.call_g7_http_interface(
                    'VEHICLE_HISTORY_TRACK_QUERY',
                    queries=queries
                )
                for x in data:
                    results['paths'].append([x.pop('lng'), x.pop('lat')])
                    results['total_distance'] += round(x['distance'] / 100)
                    x['distance'] = round(
                        results['total_distance'] / 1000, 2
                    )
                    x['time'] = datetime.fromtimestamp(
                        int(x['time'])/1000, tz=tz('Asia/Shanghai')
                    ).strftime('%Y-%m-%d %H:%M:%S')

                results['meta'].extend(data)

                if len(data) == 1000:
                    start_time = datetime.strptime(
                        data[999]['time'], '%Y-%m-%d %H:%M:%S'
                    )
                    start_time = start_time + timedelta(seconds=1)
                    start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')

                else:
                    break
            except Exception:
                results = {
                    'result': {
                        'code': '1',
                        'msg': 'g7 error'
                    }
                }
                break

        if 'total_distance' in results:
            results['total_distance'] = round(
                results['total_distance'] / 1000, 2
            )

        return Response(
            results,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='mileage')
    def get_mileage(self, request):
        page = self.paginate_queryset(
            m.Job.objects.all()
        )

        serializer = s.JobMileageSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='job-documents')
    def get_all_documents(self, request):
        page = self.paginate_queryset(
            m.Job.completed_jobs.all()
        )
        serializer = s.JobDocumentSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, url_path='documents')
    def get_documents(self, request, pk=None):
        job = self.get_object()
        serializer = s.JobDocumentSerializer(
            job,
            context={'request': request}
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='time')
    def get_time(self, request):
        page = self.paginate_queryset(
            m.Job.completed_jobs.all(),
        )

        serializer = s.JobTimeDurationSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='driving')
    def get_driving(self, request):
        pass

    @action(detail=False, url_path='previous', permission_classes=[IsDriverOrEscortUser])
    def previous_jobs(self, request):
        pass
        # serializer = s.JobDoneSerializer(
        #     request.user.jobs_as_driver.filter(
        #         finished_on__lte=timezone.now()
        #     ),
        #     many=True
        # )

        # return Response(
        #     serializer.data,
        #     status=status.HTTP_200_OK
        # )

    @action(detail=False, url_path='done', permission_classes=[IsDriverOrEscortUser])
    def done_jobs(self, request):
        """
        this api is used for retrieving the done job in driver app
        """
        page = self.paginate_queryset(
            m.Job.completed_jobs.filter(associated_drivers=request.user)
        )

        serializer = s.JobDoneSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='current', permission_classes=[IsDriverOrEscortUser])
    def progress_jobs(self, request):
        """
        this api is used for retrieving the current job in driver app
        """
        job = m.Job.progress_jobs.filter(associated_drivers=request.user).first()
        if job is not None:
            ret = s.JobCurrentSerializer(job).data
        else:
            ret = None

        return Response(
            ret,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='future', permission_classes=[IsDriverOrEscortUser])
    def future_jobs(self, request):
        """
        this api is used for retrieving future jobs in driver app
        """
        page = self.paginate_queryset(
            m.Job.pending_jobs.filter(associated_drivers=request.user)
        )

        serializer = s.JobFutureSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, url_path='update-progress', permission_classes=[IsDriverOrEscortUser])
    def progress_update(self, request, pk=None):
        """
        this api is used for update progress in driver app
        """
        job = self.get_object()

        # driver cannot perform more than 2 jobs
        if m.Job.progress_jobs.exclude(id=job.id).filter(associated_drivers=request.user).exists():
            return Response(
                {'error': 'Cannot proceed more than 2 jobs simultaneously'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # driver cannot update already finished job
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

            # set the vehicle status to in-work
            job.vehicle.status = c.VEHICLE_STATUS_INWORK
            job.vehicle.save()

            # set the driver & escrot to in-work
            driver = job.associated_drivers.first()
            escort = job.associated_escorts.first()
            driver.profile.status = c.WORK_STATUS_DRIVING
            escort.profile.status = c.WORK_STATUS_DRIVING
            driver.profile.save()
            escort.profile.save()
        else:
            current_station = job.jobstation_set.filter(
                is_completed=False
            ).first()

            sub_progress = (current_progress - c.JOB_PROGRESS_TO_LOADING_STATION) % 4
            if sub_progress == 0:
                current_station.arrived_station_on = timezone.now()
                current_station.save()
                if current_station.step == 0:
                    last_progress_finished_on = job.started_on
                else:
                    last_progress_finished_on = current_station.previous_station.departure_station_on
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
                    loading_station_arrived_on = job.jobstation_set.get(step=0).arrived_station_on

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
                    job.total_mileage = job.empty_mileage + job.heavy_mileage
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

    @action(detail=True, url_path="test/station-efence")
    def test_station_efence(self, request, pk=None):
        """
        This api is only used for test purpose
        """
        from ..core.redis import r

        job = self.get_object()
        if job.progress <= 1:
            return Response(
                {
                    'msg':
                    'enter & exit event test is only enabled for in-progress'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        event = request.query_params.get('type', 'in')
        if event == 'in':
            r.set('station_delta_distance', 10)
        elif event == 'out':
            r.set('station_delta_distance', 1000)
        return Response(
            {'msg': 'success'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="test/blackdot-efence")
    def test_black_dot_efence(self, request, pk=None):
        from ..core.redis import r

        event = request.query_params.get('type', 'in')
        if event == 'in':
            r.set('blackdot_delta_distance', 10)
        elif event == 'out':
            r.set('blackdot_delta_distance', 1000)
        return Response(
            {'msg': 'success'},
            status=status.HTTP_200_OK
        )


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
        images = request.data.pop('images', [])
        instance.man_hole = request.data.pop('man_hole', '')
        instance.branch_hole = request.data.pop('branch_hole', '')
        instance.volume = request.data.pop('volume', 0)
        instance.save()

        for image in images:
            image['job_station_product'] = instance.id
            serializer = s.JobStationProductDocumentSerializer(data=image)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response(
            {'msg': 'Successfully uploaded'},
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
        serializer = s.DriverJobReportSerializer(
            page,
            many=True
        )
        return self.get_paginated_response(serializer.data)

        return Response(
            request.user.report.all()
        )
        return request.user


class OrderReportViewSet(viewsets.ModelViewSet):

    queryset = m.OrderReport.objects.all()
    serializer_class = s.CustomerAppOrderReportSerializer

    @action(detail=False, url_path='me')
    def me(self, request):
        page = self.paginate_queryset(
            request.user.customer_profile.monthly_reports.all()
        )
        serializer = s.CustomerAppOrderReportSerializer(
            page,
            many=True
        )
        return self.get_paginated_response(serializer.data)


class LoadingStationDocumentDeleteAPIView(DestroyAPIView):
    """
    This api is used for delete loading station check document in driver app
    """
    queryset = m.LoadingStationDocument.objects.all()


class JobStationProductDocumentDeleteAPIView(DestroyAPIView):
    """
    This api is used for delete loading station check document in driver app
    """
    queryset = m.JobStationProductDocument.objects.all()
