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
from .tasks import notify_of_job_creation


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

        # send notification
        notify_of_job_creation.apply_async(
            args=[{
                'job': job.id,
                'driver': driver.id,
                'escort': escort.id
            }]
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

    def update(self, request, pk=None):
        """
         - completed order jobs cannot be updated
         - completed job cannot be updated
         - job cannot updated after loading
         - vehicle cannot be updated if the job started
         - branches and routes cannot be updated if the vehicle arrived at loading station
        """
        job = self.get_object()

        msg = ''
        if job.order.status == c.ORDER_STATUS_COMPLETE:
            msg = "Cannot update completed order's job"

        if job.progress == c.JOB_PROGRESS_COMPLETE:
            msg = "Cannot update completed job"

        if job.progress > c.JOB_PROGRESS_TO_LOADING_STATION:
            msg = "Cannot update this job because it load the product"

        if msg:
            return Response(
                {
                    'msg': msg
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

        if job.progress == c.JOB_PROGRESS_TO_LOADING_STATION and job.vehicle != vehicle:
            return Response(
                {
                    'msg': 'you canot change the vehicle'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # validate driver
        try:
            driver = User.objects.get(
                id=request.data.pop('driver', None)
            )
        except User.DoesNotExist:
            raise s.serializers.ValidationError({
                'driver': 'Such driver does not exist'
            })

        if job.progress == c.JOB_PROGRESS_TO_LOADING_STATION and job.associated_drivers.first() != driver:
            return Response(
                {
                    'msg': 'you canot change the driver'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # validate escort
        try:
            escort = User.objects.get(
                id=request.data.pop('escort', None)
            )
        except User.DoesNotExist:
            raise s.serializers.ValidationError({
                'escort': 'Such escort does not exist'
            })

        if job.progress == c.JOB_PROGRESS_TO_LOADING_STATION and job.driver.associated_escorts.first() != escort:
            return Response(
                {
                    'msg': 'you canot change the escort'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

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

        old_arranged_products = {}
        for jobstationproduct in job.jobstation_set.first().jobstationproduct_set.all():
            product_id = jobstationproduct.product.id
            if product_id not in old_arranged_products:
                old_arranged_products[product_id] = {
                    'branch': [jobstationproduct.branch],
                    'mission_weight': jobstationproduct.mission_weight
                }
            else:
                old_arranged_products[product_id]['mission_weight'] += jobstationproduct.mission_weight
                old_arranged_products[product_id]['branch'].append(jobstationproduct.branch)

        for product_id, arranged_product in arranged_products.items():
            order_product = get_object_or_404(m.OrderProduct, order=job.order, product__id=product_id)

            remaining_product_weight = order_product.weight - order_product.arranged_weight
            if product_id in old_arranged_products:
                remaining_product_weight += old_arranged_products[product_id]['mission_weight']

            if remaining_product_weight < arranged_product['mission_weight']:
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
        if not job.order.is_same_station:
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
        job.vehicle = vehicle
        job.routes = route_ids
        job.save()

        job.stations.clear()

        for product_id, old_arranged_product in old_arranged_products.items():
            order_product = get_object_or_404(m.OrderProduct, order=job.order, product__id=product_id)
            order_product.arranged_weight -= old_arranged_product['mission_weight']
            order_product.save()

        for product_id, arranged_product in arranged_products.items():
            order_product = get_object_or_404(m.OrderProduct, order=job.order, product__id=product_id)
            order_product.arranged_weight += arranged_product['mission_weight']
            order_product.save()

        job_loading_station = m.JobStation.objects.create(
            job=job, station=job.order.loading_station, step=0
        )
        job_quality_station = m.JobStation.objects.create(
            job=job, station=job.order.quality_station, step=1
        )
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

        if job.associated_drivers.first() != driver:
            m.JobDriver.objects.create(job=job, driver=driver)

        if job.associated_escorts.first() != escort:
            m.JobEscort.objects.create(job=job, escort=escort)

        return Response(
            s.JobAdminSerializer(job).data,
            status=status.HTTP_200_OK
        )

    def destroy(self, request, pk=None):
        # job can be deleted only if driver didn't start the job
        job = self.get_object()
        if job.progress != c.JOB_PROGRESS_NOT_STARTED:
            return Response(
                {
                    'msg': 'Cannot delete this job'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        arranged_products = {}
        for jobstationproduct in job.jobstation_set.first().jobstationproduct_set.all():
            product_id = jobstationproduct.product.id
            if product_id not in arranged_products:
                arranged_products[product_id] = {
                    'branch': [jobstationproduct.branch],
                    'mission_weight': jobstationproduct.mission_weight
                }
            else:
                arranged_products[product_id]['mission_weight'] += jobstationproduct.mission_weight
                arranged_products[product_id]['branch'].append(jobstationproduct.branch)

        for product_id, arranged_product in arranged_products.items():
            order_product = get_object_or_404(m.OrderProduct, order=job.order, product__id=product_id)
            order_product.arranged_weight -= arranged_product['mission_weight']
            order_product.save()

        job.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, url_path='done-job')
    def get_done_job(self, request, pk=None):
        job = self.get_object()
        if job.progress != c.JOB_PROGRESS_COMPLETE:
            return Response(
                {
                    'msg': 'Cannot read this job because this job is not complete yet'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            s.JobDoneSerializer(job, context={'request': request}).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], url_path='upload-loading-check')
    def upload_loading_station_check(self, request, pk=None):
        job = self.get_object()
        if job.progress == c.JOB_PROGRESS_NOT_STARTED:
            return Response(
                {
                    'msg': 'You cannot upload because this job is not started yet'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        images = request.data.pop('images', [])
        product = get_object_or_404(Product, id=request.data.get('product').get('id'))

        loading_check, created = m.LoadingStationProductCheck.objects.get_or_create(
            job=job, product=product
        )

        loading_check.weight = request.data.pop('weight')
        loading_check.save()

        for image in images:
            if image.get('id', None):
                continue
            image['loading_station'] = loading_check.id
            serializer = s.LoadingStationDocumentSerializer(data=image)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response(
            s.LoadingStationProductCheckSerializer(
                loading_check,
                context={'request': request}
            ).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], url_path='upload-quality-check')
    def upload_quality_check(self, request, pk=None):
        job = self.get_object()
        if job.progress == c.JOB_PROGRESS_NOT_STARTED:
            return Response(
                {
                    'msg': 'You cannot upload because this job is not started yet'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

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

        job_qualitystation_product.weight = request.data.pop('weight')
        job_qualitystation_product.volume = request.data.pop('volume')
        job_qualitystation_product.man_hole = request.data.pop('man_hole')
        job_qualitystation_product.branch_hole = request.data.pop('branch_hole')
        job_qualitystation_product.save()

        for image in images:
            if image.get('id', None):
                continue
            image['job_station_product'] = job_qualitystation_product.id
            serializer = s.JobStationProductDocumentSerializer(data=image)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        ret = {
            'branch': branch,
            'density': quality_check.density,
            'additive': quality_check.additive,
            'volume': job_qualitystation_product.volume,
            'man_hole': job_qualitystation_product.man_hole,
            'branch_hole': job_qualitystation_product.branch_hole,
            'images': s.ShortJobStationProductDocumentSerializer(
                job_qualitystation_product.images.all(),
                context={'request': request},
                many=True
            ).data
        }
        return Response(
            ret,
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

    @action(detail=False, url_path='done-jobs')
    def done_jobs(self, request):
        """
        this api is used for retrieving the done job in driver app
        """
        page = self.paginate_queryset(
            m.Job.completed_jobs.all()
        )

        serializer = s.JobSerializer(
            page, context={'request': request}, many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='me/done-jobs', permission_classes=[IsDriverOrEscortUser])
    def driver_done_jobs(self, request):
        """
        this api is used for retrieving the done job in driver app
        """
        page = self.paginate_queryset(
            m.Job.completed_jobs.filter(associated_drivers=request.user)
        )

        serializer = s.JobDoneSerializer(
            page, context={'request': request}, many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='me/current-jobs', permission_classes=[IsDriverOrEscortUser])
    def current_jobs(self, request):
        """
        this api is used for retrieving the current job in driver app
        """
        job = m.Job.progress_jobs.filter(associated_drivers=request.user).first()
        if job is not None:
            ret = s.JobCurrentSerializer(job).data
        else:
            ret = {}

        return Response(
            ret,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='me/future-jobs', permission_classes=[IsDriverOrEscortUser])
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

            job_driver = m.JobDriver.objects.get(job=job, driver=request.user)
            job_driver.started_on = timezone.now()
            job_driver.save()

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

                    job_driver = m.JobDriver.objects.get(job=job, driver=request.user)
                    job_driver.finished_on = timezone.now()
                    job_driver.save()

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
        if instance.job_station.job.progress == c.JOB_PROGRESS_NOT_STARTED:
            return Response(
                {
                    'msg': 'You cannot upload because this job is not started yet'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

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

        ret = {
            'branch': instance.branch,
            'volume': instance.volume,
            'images': s.ShortJobStationProductDocumentSerializer(
                instance.images.all(),
                context={'request': request},
                many=True
            ).data
        }
        return Response(
            ret,
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
