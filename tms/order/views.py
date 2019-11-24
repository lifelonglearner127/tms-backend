import json
from datetime import datetime, timedelta
from pytz import timezone as tz
import requests

from django.conf import settings
from django.db import connection
from django.db.models import Q, Max
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.generics import DestroyAPIView
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_renderer_xlsx.mixins import XLSXFileMixin
from drf_renderer_xlsx.renderers import XLSXRenderer

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# constants
from ..core import constants as c
from ..core.utils import get_branches

# permissions
from ..core.permissions import (
    IsDriverOrEscortUser, IsCustomerUser, OrderPermission
)

# models
from . import models as m
from ..account.models import User
from ..info.models import Product
from ..route.models import Route
from ..vehicle.models import Vehicle, VehicleWorkerBind

# serializers
from . import serializers as s
from ..vehicle.serializers import VehiclePositionSerializer

# views
from ..core.views import TMSViewSet

# other
from ..g7.interfaces import G7Interface
from .tasks import (
    notify_order_changes,
    notify_of_job_creation, notify_of_job_changes,
    notify_of_job_deleted, notify_of_worker_change_after_job_start,
    notify_of_driver_or_escort_changes_before_job_start
)


channel_layer = get_channel_layer()


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
    queryset = m.Order.availables.all()
    serializer_class = s.OrderSerializer
    permission_classes = [OrderPermission]

    def create(self, request):

        context = {
            'products': request.data.pop('products'),
            'assignee': request.data.pop('assignee', None),
            'loading_station': request.data.pop('loading_station'),
            'quality_station': request.data.pop('quality_station')
        }
        data = request.data
        if request.user.user_type == c.USER_TYPE_CUSTOMER:
            context['customer'] = {
                'id': request.user.customer_profile.id
            }
            data['order_source'] = c.ORDER_SOURCE_CUSTOMER
        else:
            context['customer'] = request.data.pop('customer')
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
        order = self.get_object()
        if order.status == c.ORDER_STATUS_COMPLETE or order.arrangement_status == c.TRUCK_ARRANGEMENT_STATUS_COMPLETE:
            return Response(
                {
                    'msg': 'Cannot update the order because of order status or its arranegement status'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.user.user_type == c.USER_TYPE_CUSTOMER and requests.user.customer_profile != order.customer:
            return Response(
                {
                    'msg': 'Cannot update the order'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        order_products_data = request.data.pop('products', None)
        if order_products_data is None:
            return Response(
                {
                    'products': 'Order Product data is missing'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # check if loading station exists
        loading_station_data = request.data.pop('loading_station', None)
        if loading_station_data is None:
            return Response(
                {
                    'loading_station': 'Loading station data is missing'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        loading_station = get_object_or_404(
            m.Station,
            id=loading_station_data.get('id'),
            station_type=c.STATION_TYPE_LOADING_STATION
        )

        # check if quality station exists
        quality_station_data = request.data.pop('quality_station', None)
        if quality_station_data is None:
            return Response(
                {
                    'quality_station': 'Quality station data is missing'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        quality_station = get_object_or_404(
            m.Station,
            id=quality_station_data.get('id'),
            station_type=c.STATION_TYPE_QUALITY_STATION
        )

        # check if assignee exists
        assignee_data = request.data.pop('assignee', None)
        if assignee_data is None:
            assignee = None
        else:
            assignee = get_object_or_404(
                s.StaffProfile,
                id=assignee_data.get('id')
            )

        # check if customer exists
        if request.user.user_type == c.USER_TYPE_CUSTOMER:
            customer = request.user.customer_profile
            update_from_staff = False
        else:
            update_from_staff = True
            customer_data = request.data.pop('customer', None)
            if customer_data is None:
                raise s.serializers.ValidationError({
                    'customer': 'Customer data is missing'
                })

            customer = get_object_or_404(
                m.CustomerProfile,
                id=customer_data.get('id')
            )

        is_same_station = request.data.get('is_same_station', False)

        if order.arrangement_status == c.TRUCK_ARRANGEMENT_STATUS_INPROGRESS:
            error = False

            if not error and customer != order.customer:
                msg = 'Cannot change customer because the job already created'
                error = True

            if not error and loading_station != order.loading_station:
                msg = 'Cannot change loading station because the job already created'
                error = True

            if not error and quality_station != order.quality_station:
                msg = 'Cannot change quality station because the job already created'
                error = True

            if not error and is_same_station != order.is_same_station:
                msg = 'Cannot change station meta because the job already created'
                error = True

            if not error:
                for order_product in order.orderproduct_set.all():
                    if not order_product.arranged_weight:
                        continue

                    existing_order_product = list(
                        filter(
                            lambda x: 'product' in x and x['product']['id'] == order_product.product.id,
                            order_products_data
                        )
                    )
                    if not existing_order_product:
                        msg = 'Cannot delete the product that is already arranged'
                        error = True
                        break

                    if order_product.arranged_weight > float(existing_order_product[0]['weight']):
                        msg = f'{order_product.product.name} is already arranged {order_product.arranged_weight}'
                        'so cannot update'
                        error = True
                        break

            if error:
                return Response(
                    {
                        'msg': msg
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        previous_customer = order.customer
        is_same_customer = previous_customer == customer
        order.assignee = assignee
        order.customer = customer
        order.loading_station = loading_station
        order.quality_station = quality_station

        for key, value in request.data.items():
            setattr(order, key, value)

        order.save()

        old_products = set(order.products.values_list('id', flat=True))
        new_products = set()

        # save models
        for order_product_data in order_products_data:
            product_data = order_product_data.pop('product', None)
            product = get_object_or_404(
                m.Product,
                id=product_data.get('id', None)
            )

            new_products.add(product.id)
            if product.id not in old_products:
                order_product = m.OrderProduct.objects.create(
                    order=order,
                    product=product,
                    weight=float(order_product_data.get('weight')),
                    is_split=order_product_data.get('is_split'),
                    is_pump=order_product_data.get('is_pump'),
                )
            else:
                order_product = get_object_or_404(
                    m.OrderProduct,
                    order=order,
                    product=product
                )

                order_product.weight = float(order_product_data.get('weight'))
                order_product.is_split = order_product_data.get('is_split')
                order_product.is_pump = order_product_data.get('is_pump')
                order_product.save()

        m.OrderProduct.objects.filter(
            order=order,
            product__id__in=old_products.difference(new_products)
        ).delete()

        if is_same_customer:
            if update_from_staff:
                notify_order_changes.apply_async(
                    args=[{
                        'order': order.id,
                        'customer_user_id': customer.user.id,
                        'message_type': c.CUSTOMER_NOTIFICATION_UPDATE_ORDER
                    }]
                )
        else:
            notify_order_changes.apply_async(
                args=[{
                    'order': order.id,
                    'customer_user_id': customer.user.id,
                    'message_type': c.CUSTOMER_NOTIFICATION_NEW_ORDER
                }]
            )
            notify_order_changes.apply_async(
                args=[{
                    'order': order.id,
                    'customer_user_id': previous_customer.user.id,
                    'message_type': c.CUSTOMER_NOTIFICATION_DELETE_ORDER
                }]
            )

        return Response(
            s.OrderSerializer(order).data,
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

    def destroy(self, request, pk=None):
        order = self.get_object()
        if order.arrangement_status != c.TRUCK_ARRANGEMENT_STATUS_PENDING:
            return Response(
                {
                    'msg': 'You cannot delete the order because it is under working'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.user.user_type != c.USER_TYPE_CUSTOMER:
            s.notify_order_changes.apply_async(
                args=[{
                    'order': order.id,
                    'customer_user_id': order.customer.user.id,
                    'message_type': c.CUSTOMER_NOTIFICATION_DELETE_ORDER
                }]
            )

        order.is_deleted = True
        order.save()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, url_path='job', methods=['post'])
    def create_job(self, request, pk=None):
        """
        payload:
        {
            vehicle: {},
            driver: {},
            escort: {},
            routes: {},
            restPlace: {}
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

        # validate rest place
        rest_place = request.data.pop('rest_place', None)
        if rest_place is not None:
            try:
                rest_place = m.Station.parkingstations.get(
                    id=rest_place
                )
            except m.Station.DoesNotExist:
                raise s.serializers.ValidationError({
                    'station': 'Such station does not exist'
                })

        # check if branch weight exceed vehicle branch weight
        errors = {}
        transport_unit_prices = {}
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
                transport_unit_price = float(unloading_station_data.get('transport_unit_price'))
                unloading_station_weight = float(unloading_station_data.get('mission_weight', 0))
                branch_weight = branch_weight - unloading_station_weight

                transport_unit_prices[unloading_station_id] = transport_unit_price
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
        job = m.Job.objects.create(order=order, vehicle=vehicle, routes=route_ids, rest_place=rest_place)
        m.JobWorker.objects.create(job=job, worker=driver, worker_type=c.WORKER_TYPE_DRIVER)
        m.JobWorker.objects.create(job=job, worker=escort, worker_type=c.WORKER_TYPE_ESCORT)

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
                job=job, station=route.end_point, step=route_index+2,
                transport_unit_price=transport_unit_prices[route.end_point.id]
            )
            for job_product in job_products[route.end_point.id]:
                m.JobStationProduct.objects.create(
                    job_station=job_station,
                    product=get_object_or_404(Product, id=job_product['product']),
                    branch=job_product['branch'],
                    due_time=job_product['due_time'],
                    mission_weight=job_product['mission_weight']
                )

        for orderproduct in order.orderproduct_set.all():
            if order_product.arranged_weight < order_product.weight:
                break
        else:
            order.arrangement_status = c.TRUCK_ARRANGEMENT_STATUS_COMPLETE
            order.save()

        if order.arrangement_status == c.TRUCK_ARRANGEMENT_STATUS_PENDING:
            order.arrangement_status = c.TRUCK_ARRANGEMENT_STATUS_INPROGRESS
            order.save()

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
            order.jobs.order_by('-created'),
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
        queryset = m.Order.availables.filter(
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

    @action(detail=True, url_path='payments')
    def get_order_payments(self, request, pk=None):
        order = self.get_object()
        page = self.paginate_queryset(
            m.OrderPayment.objects.filter(
                job_station__job__order=order
            )
        )
        serializer = s.OrderPaymentSerializer(
            page,
            many=True
        )
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
        """Update the job if according to update logic

         - completed job cannot be updated
         - vehicle cannot be updated once the job started
         - driver, escort cannot be updated in this context once the job started
         - job cannot updated after loading
         - branches and routes cannot be updated if the vehicle arrived at loading station
        """
        job = self.get_object()
        is_updated_job = False

        # completed order jobs cannot be updated
        if job.progress == c.JOB_PROGRESS_COMPLETE:
            return Response(
                {
                    'msg': 'Cannot update completed job"'
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

        # vehicle cannot be updated once the job started
        if job.progress >= c.JOB_PROGRESS_TO_LOADING_STATION and job.vehicle != vehicle:
            return Response(
                {
                    'msg': 'you canot change the vehicle'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # validate driver
        # driver, escort cannot be updated in this context once the job started
        current_driver = job.jobworker_set.filter(worker_type=c.WORKER_TYPE_DRIVER).first().worker
        current_escort = job.jobworker_set.filter(worker_type=c.WORKER_TYPE_ESCORT).first().worker

        try:
            new_driver = User.objects.get(
                id=request.data.pop('driver', None)
            )
        except User.DoesNotExist:
            raise s.serializers.ValidationError({
                'driver': 'Such driver does not exist'
            })

        if job.progress >= c.JOB_PROGRESS_TO_LOADING_STATION and current_driver != new_driver:
            return Response(
                {
                    'msg': 'You cannot change the driver in this context'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # validate escort
        try:
            new_escort = User.objects.get(
                id=request.data.pop('escort', None)
            )
        except User.DoesNotExist:
            raise s.serializers.ValidationError({
                'escort': 'Such escort does not exist'
            })

        if job.progress >= c.JOB_PROGRESS_TO_LOADING_STATION and current_escort != new_escort:
            return Response(
                {
                    'msg': 'you canot change the escort in this context'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # check if branch weight exceed vehicle branch weight
        errors = {}
        transport_unit_prices = {}
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
                transport_unit_price = float(unloading_station_data.get('transport_unit_price', 0))
                unloading_station_weight = float(unloading_station_data.get('mission_weight', 0))
                branch_weight = branch_weight - unloading_station_weight

                transport_unit_prices[unloading_station_id] = transport_unit_price
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

        old_vehicle = job.vehicle.plate_num
        old_branches = get_branches(job)

        job_loading_station = job.jobstation_set.first()
        job_quality_station = job.jobstation_set.get(step=1)
        new_loading_station_branches = {
            job_loading_station_product['branch'] for job_loading_station_product in job_products['total']
        }
        old_loading_station_branches = set(
            job_loading_station.jobstationproduct_set.values_list('branch', flat=True)
        )

        difference_products = old_loading_station_branches.difference(new_loading_station_branches)
        if difference_products:
            if job.progress >= c.JOB_PROGRESS_ARRIVED_AT_LOADING_STATION:
                return Response(
                    {
                        'msg': '当前到达装货地，所以不能修装货货品和数量'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                job_loading_station.jobstationproduct_set.filter(
                    branch__in=difference_products
                ).delete()
                job_quality_station.jobstationproduct_set.filter(
                    branch__in=difference_products
                ).delete()

        for job_station_product in job_products['total']:
            job_loading_station_product =\
                job_loading_station.jobstationproduct_set.filter(
                    branch=job_station_product['branch']
                ).first()

            if job_loading_station_product is None:
                if job.progress >= c.JOB_PROGRESS_ARRIVED_AT_LOADING_STATION:
                    return Response(
                        {
                            'msg': '当前到达装货地，所以不能修装货货品和数量'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                else:
                    is_updated_job = True
                    new_added_product = get_object_or_404(Product, id=job_station_product['product'])
                    m.JobStationProduct.objects.create(
                        job_station=job_loading_station,
                        product=new_added_product,
                        branch=job_station_product['branch'],
                        mission_weight=job_station_product['mission_weight']
                    )
                    m.JobStationProduct.objects.create(
                        job_station=job_quality_station,
                        product=new_added_product,
                        branch=job_station_product['branch'],
                        mission_weight=job_station_product['mission_weight']
                    )
            else:
                if job_loading_station_product.product.id != job_station_product['product']\
                   or job_loading_station_product.mission_weight != job_station_product['mission_weight']:

                    if job.progress >= c.JOB_PROGRESS_ARRIVED_AT_LOADING_STATION:
                        return Response(
                            {
                                'msg': '当前到达装货地，所以不能修装货货品和数量'
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    else:
                        is_updated_job = True
                        new_added_product = get_object_or_404(Product, id=job_station_product['product'])
                        job_loading_station_product.product = new_added_product
                        job_loading_station_product.mission_weight = job_station_product['mission_weight']
                        job_loading_station_product.save()

                        job_quality_station_product = job_quality_station.jobstationproduct_set.filter(
                            branch=job_station_product['branch']
                        ).first()
                        job_quality_station_product.product = new_added_product
                        job_quality_station_product.mission_weight = job_station_product['mission_weight']
                        job_quality_station_product.save()

        new_unloading_stations = [route.end_point for route in routes]
        old_unloading_stations = [
            job_station for job_station in job.jobstation_set.filter(step__gte=2).order_by('step')
        ]
        run_job_stations = [station for station in old_unloading_stations if station.is_completed]
        next_job_station = None
        if job.progress >= c.JOB_PROGRESS_TO_UNLOADING_STATION:
            next_job_station = old_unloading_stations[len(run_job_stations)]

        if next_job_station\
           and [station.station for station in run_job_stations] \
           != new_unloading_stations[:len(run_job_stations)]:
            run_station_names = [station.station.name for station in run_job_stations]
            run_station_names.insert(0, job.order.quality_station.name)
            run_station_names.insert(0, job.order.loading_station.name)
            return Response(
                {
                    'msg': 'You cannot update the routes like this because the driver is already run {}'
                    'and now heading to {}'
                    .format(
                        ' -> '.join(run_station_names),
                        next_job_station.station.name
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        for run_station in run_job_stations:
            unloading_station_products = job_products.get(run_station.station.id, None)
            if unloading_station_products is None:
                return Response(
                    {
                        'msg': 'You cannot delete the already delivered products'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                new_unloading_station_branches = {
                    unloading_station_product['branch'] for unloading_station_product in unloading_station_products
                }
                old_unloading_station_branches = set(
                    run_station.jobstationproduct_set.values_list('branch', flat=True)
                )

                difference_products = old_unloading_station_branches.difference(new_unloading_station_branches)
                if difference_products:
                    return Response(
                        {
                            'msg': 'You cannot update the already delievered products'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                for unloading_station_product in unloading_station_products:
                    run_station_product = run_station.jobstationproduct_set.filter(
                        branch=unloading_station_product['branch']
                    ).first()

                    if run_station_product.mission_weight != unloading_station_product['mission_weight']\
                       or run_station_product.product.id != unloading_station_product['product']:
                        return Response(
                            {
                                'msg': 'You cannot change the delivered product details'
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

        job.jobstation_set.filter(
            station__id__in=[station.station.id for station in old_unloading_stations]).delete()
        for new_station_index, new_station in enumerate(new_unloading_stations):
            is_updated_job = True
            job_station = m.JobStation.objects.create(
                job=job,
                station=new_station,
                step=new_station_index+2,
                transport_unit_price=transport_unit_prices[new_station.id]
            )
            for job_product in job_products[new_station.id]:
                m.JobStationProduct.objects.create(
                    job_station=job_station,
                    product=get_object_or_404(Product, id=job_product['product']),
                    branch=job_product['branch'],
                    due_time=job_product['due_time'],
                    mission_weight=job_product['mission_weight']
                )

        if job.vehicle != vehicle or job.routes != route_ids:
            is_updated_job = True

        if is_updated_job:
            job.vehicle = vehicle
            job.routes = route_ids
            job.save()

            for product_id, old_arranged_product in old_arranged_products.items():
                order_product = get_object_or_404(m.OrderProduct, order=job.order, product__id=product_id)
                order_product.arranged_weight -= old_arranged_product['mission_weight']
                order_product.save()

            for product_id, arranged_product in arranged_products.items():
                order_product = get_object_or_404(m.OrderProduct, order=job.order, product__id=product_id)
                order_product.arranged_weight += arranged_product['mission_weight']
                order_product.save()
            if current_driver == new_driver and current_escort == new_escort:
                notify_of_job_changes.apply_async(
                    args=[{
                        'job': job.id,
                        'driver': current_driver.id,
                        'escort': current_escort.id
                    }]
                )
            else:
                if current_driver != new_driver:
                    m.JobWorker.drivers.get(job=job).delete()
                    m.JobWorker.objects.create(job=job, worker=new_driver, worker_type=c.WORKER_TYPE_DRIVER)

                if current_escort != new_escort:
                    m.JobWorker.escorts.get(job=job).delete()
                    m.JobWorker.objects.create(job=job, worker=new_escort, worker_type=c.WORKER_TYPE_ESCORT)

                notify_of_driver_or_escort_changes_before_job_start.apply_async(
                    args=[{
                        'job': job.id,
                        'current_driver': current_driver.id,
                        'new_driver': new_driver.id,
                        'current_escort': current_escort.id,
                        'new_escort': new_escort.id,
                        'old_vehicle': old_vehicle,
                        'old_branches': old_branches,
                        'is_driver_updated': current_driver != new_driver,
                        'is_escort_updated':  current_escort != new_escort
                    }]
                )

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

        arranged_product_count = 0
        for orderproduct in job.order.orderproduct_set.all():
            if order_product.arranged_weight > 0 and order_product.arranged_weight < order_product.weight:
                arranged_product_count += 1
                if job.order.arrangement_status == c.TRUCK_ARRANGEMENT_STATUS_COMPLETE:
                    job.order.arrangement_status = c.TRUCK_ARRANGEMENT_STATUS_INPROGRESS
                    job.order.save()
                    break

        if order_product.arranged_weight == 0:
            if job.order.arrangement_status != c.TRUCK_ARRANGEMENT_STATUS_PENDING:
                job.order.arrangement_status = c.TRUCK_ARRANGEMENT_STATUS_PENDING
                job.order.save()

        notify_of_job_deleted.apply_async(
            args=[{
                'job': job.id,
                'vehicle': job.vehicle.plate_num,
                'driver': job.jobworker_set.filter(worker_type=c.WORKER_TYPE_DRIVER).first().worker.id,
                'escort': job.jobworker_set.filter(worker_type=c.WORKER_TYPE_ESCORT).first().worker.id,
                'customer': job.order.customer.id,
                'loading_station': job.order.loading_station.address,
                'branches': get_branches(job),
                'rest_place': job.rest_place.address if job.rest_place is not None else '-'
            }]
        )

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
        quality_check.volume = request.data.pop('volume')
        quality_check.save()

        job_qualitystation = job.jobstation_set.all()[1]

        job_qualitystation_product = get_object_or_404(
            m.JobStationProduct, job_station=job_qualitystation, branch=branch
        )

        job_qualitystation_product.weight = request.data.pop('weight')
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
            'volume': quality_check.volume,
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

    @action(detail=False, url_path='done-jobs')
    def done_jobs(self, request):
        """
        this api is used for retrieving the done job in driver app
        """
        page = self.paginate_queryset(
            m.Job.completed_jobs.all()
        )

        serializer = s.JobDoneSerializer(
            page, context={'request': request}, many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='me/done-jobs', permission_classes=[IsDriverOrEscortUser])
    def driver_done_jobs(self, request):
        """
        this api is used for retrieving the done job in driver app
        """
        page = self.paginate_queryset(
            m.Job.completed_jobs.filter(associated_workers=request.user)
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
        job_worker = m.JobWorker.objects.filter(
            worker=request.user, is_active=True, job__progress__gt=c.JOB_PROGRESS_NOT_STARTED
        ).first()
        if job_worker:
            ret = s.JobCurrentSerializer(job_worker.job).data
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
            m.JobWorker.objects.filter(
                worker=request.user,
                job__progress__gte=c.JOB_PROGRESS_NOT_STARTED,
                is_active=False
            )
        )
        jobs = [jobworker.job for jobworker in page]

        serializer = s.JobFutureSerializer(jobs, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, url_path='confirm-job-change')
    def confirm_job_change(self, request, pk=None):
        job = self.get_object()
        next_worker = job.jobworker_set.filter(
            worker=request.user,
            finished_on=None
        ).first()
        if not next_worker:
            return Response(
                {
                    'error': 'You are not permitted to proceed this job'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        next_worker.started_on = timezone.now()
        next_worker.is_active = True
        next_worker.save()
        return Response(
            s.JobCurrentSerializer(next_worker.job).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, url_path='update-progress', permission_classes=[IsDriverOrEscortUser])
    def progress_update(self, request, pk=None):
        """
        this api is used for update progress in driver app
        """
        job = self.get_object()
        meta_numbers = []
        worker = request.user

        # 1. Check if this user is authorized to perform this job
        candidate_job_driver = job.jobworker_set.filter(worker_type=c.WORKER_TYPE_DRIVER).first()
        candidate_job_escort = job.jobworker_set.filter(worker_type=c.WORKER_TYPE_ESCORT).first()
        if worker != candidate_job_driver.worker and worker != candidate_job_escort.worker:
            return Response(
                {
                    'error': 'You are not permitted to proceed this job yet.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # 2. check if this worker is on vehicle
        vehicle_bind = VehicleWorkerBind.objects.filter(vehicle=job.vehicle, worker=worker).first()
        if vehicle_bind is None or vehicle_bind.get_off is not None or\
           (vehicle_bind.get_off is None and vehicle_bind.vehicle != job.vehicle):
            return Response(
                {'error': 'You need to get on vehicle first'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. check if partner is on vehicle together
        if worker.user_type == c.WORKER_TYPE_DRIVER:
            partner = candidate_job_escort.worker
        else:
            partner = candidate_job_driver.worker

        vehicle_bind = VehicleWorkerBind.objects.filter(vehicle=job.vehicle, worker=partner).first()
        if vehicle_bind is None or vehicle_bind.get_off is not None or\
           (vehicle_bind.get_off is None and vehicle_bind.vehicle != job.vehicle):
            return Response(
                {
                    'error': 'Your partner {} - {} need to get on vehicle first'.format(
                        partner.user_type, partner.name
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4. check if worker and its partner are free from other job
        if m.JobWorker.objects.exclude(job=job).filter(
            job__progress__gt=c.JOB_PROGRESS_NOT_STARTED,
            worker=worker,
            is_active=True
        ).exists():
            return Response(
                {'error': 'This job cannot be proceed because you are in other work'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if m.JobWorker.objects.exclude(job=job).filter(
            job__progress__gt=c.JOB_PROGRESS_NOT_STARTED,
            worker=partner,
            is_active=True
        ).exists():
            return Response(
                {
                    'error': 'This job cannot be proceed because your partner is in other work',
                },
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

            active_job_driver = job.jobworker_set.filter(
                worker_type=c.WORKER_TYPE_DRIVER
            ).first()
            active_job_driver.is_active = True
            active_job_driver.started_on = timezone.now()
            active_job_driver.save()

            active_job_escort = job.jobworker_set.filter(
                worker_type=c.WORKER_TYPE_ESCORT
            ).first()
            active_job_escort.is_active = True
            active_job_escort.started_on = timezone.now()
            active_job_escort.save()
            last_progress_finished_on = None
        else:
            current_station = job.jobstation_set.filter(
                is_completed=False
            ).first()

            sub_progress = (current_progress - c.JOB_PROGRESS_TO_LOADING_STATION) % 4

            if current_station is not None and current_station.previous_station is not None:
                for product in current_station.previous_station.jobstationproduct_set.all():
                    meta_numbers.append({
                        'branch': product.branch,
                        'man_hole': product.man_hole,
                        'branch_hole': product.branch_hole
                    })

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

                if current_station.step >= 2:
                    m.OrderPayment.objects.create(job_station=current_station)

                if not current_station.has_next_station:
                    job.progress = c.JOB_PROGRESS_COMPLETE
                    job.finished_on = timezone.now()

                    active_job_driver = job.jobworker_set.filter(
                        worker_type=c.WORKER_TYPE_DRIVER, is_active=True
                    ).first()
                    active_job_driver.finished_on = timezone.now()
                    active_job_driver.is_active = False
                    active_job_driver.save()

                    active_job_escort = job.jobworker_set.filter(
                        worker_type=c.WORKER_TYPE_ESCORT, is_active=True
                    ).first()
                    active_job_escort.finished_on = timezone.now()
                    active_job_escort.is_active = False
                    active_job_escort.save()

                    # update job empty mileage
                    loading_station_arrived_on = job.jobstation_set.get(step=0).arrived_station_on

                    empty_mileage_queries = {
                        'plate_num':
                            job.vehicle.plate_num,
                        'from':
                            job.started_on.strftime('%Y-%m-%d %H:%M:%S'),
                        'to':
                            loading_station_arrived_on.strftime(
                                '%Y-%m-%d %H:%M:%S'
                            )
                    }
                    heavy_mileage_queries = {
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
                    try:
                        data = G7Interface.call_g7_http_interface(
                            'VEHICLE_GPS_TOTAL_MILEAGE_INQUIRY',
                            queries=empty_mileage_queries
                        )
                        job.empty_mileage = data['total_mileage'] / (100 * 1000)
                        data = G7Interface.call_g7_http_interface(
                            'VEHICLE_GPS_TOTAL_MILEAGE_INQUIRY',
                            queries=heavy_mileage_queries
                        )
                        empty_mileage = data['total_mileage'] / (100 * 1000)
                        heavy_mileage = data['total_mileage'] / (100 * 1000)
                    except Exception:
                        empty_mileage = 0
                        heavy_mileage = 0

                    job.empty_mileage = empty_mileage
                    job.heavy_mileage = heavy_mileage
                    job.total_mileage = job.empty_mileage + job.heavy_mileage
                    job.highway_mileage = 0
                    job.normalway_mileage = 0
                    job.save()

        if job.progress != c.JOB_PROGRESS_COMPLETE:
            job.progress = current_progress + 1
            job.save()

        ret = {
            'progress': job.progress,
            'last_progress_finished_on': last_progress_finished_on,
        }
        if len(meta_numbers):
            ret['meta_numbers'] = meta_numbers

        if partner.channel_name:
            async_to_sync(channel_layer.send)(
                partner.channel_name,
                {
                    'type': 'notify',
                    'data': json.dumps({
                        'msg_type': c.DRIVER_NOTIFICATION_PROGRESS_SYNC,
                        'message': 'job updated'
                    })
                }
            )

        return Response(
            ret,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], url_path='change-worker')
    def change_worker(self, request, pk=None):
        job = self.get_object()
        workers_data = request.data.pop('workers', [])
        start_due_time = request.data.pop('start_due_time', None)
        start_place = request.data.pop('start_place', None)

        new_driver = None
        new_escort = None
        for worker_data in workers_data:
            worker_type = worker_data.get('worker_type', c.WORKER_TYPE_DRIVER)
            worker = get_object_or_404(m.User, id=worker_data.get('worker'), user_type=worker_type)
            if worker_type == c.WORKER_TYPE_DRIVER:
                new_driver = worker
            else:
                new_escort = worker

            m.JobWorker.objects.create(
                job=job,
                worker=worker,
                start_due_time=start_due_time,
                start_place=start_place,
                worker_type=worker_type
            )

        current_driver = job.jobworker_set.filter(worker_type=c.WORKER_TYPE_DRIVER).first()
        current_escort = job.jobworker_set.filter(worker_type=c.WORKER_TYPE_ESCORT).first()

        notify_of_worker_change_after_job_start.apply_async(
                args=[{
                    'job': job.id,
                    'current_driver': current_driver.worker.id,
                    'current_escort': current_escort.worker.id,
                    'new_driver': new_driver.id if new_driver else None,
                    'new_escort': new_escort.id if new_escort else None,
                    'change_place': start_place,
                    'change_time': start_due_time
                }]
            )

        return Response(
            {
                'msg': 'Successfully finished'
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, url_path='workers')
    def get_workers(self, requests, pk=None):
        job = self.get_object()
        workers = job.jobworker_set.order_by('assigned_on')
        return Response(
            s.ShortJobWorkerSerializer(workers, many=True).data,
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

    @action(detail=False, url_path='report/workdiary')
    def report_workdiary(self, request):
        query_filter = Q()
        year = self.request.query_params.get('year', None)
        if year is not None:
            query_filter &= Q(started_on__year=year)

        month = self.request.query_params.get('month', None)
        if month is not None:
            query_filter &= Q(started_on__month=month)

        queryset = m.Job.completed_jobs.filter(query_filter)

        page = self.paginate_queryset(queryset)
        serializer = s.JobWorkDiaryReportSerializer(
            page,
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='report/workdiary-time-schema')
    def report_workdiary_time_class_table_schema(self, request):
        query_filter = Q()
        year = self.request.query_params.get('year', None)
        if year is not None:
            query_filter &= Q(started_on__year=year)

        month = self.request.query_params.get('month', None)
        if month is not None:
            query_filter &= Q(started_on__month=month)

        queryset = m.Job.completed_jobs.filter(query_filter)

        page = self.paginate_queryset(queryset)
        max_step = m.JobStation.objects.filter(job__in=page).aggregate(Max('step'))
        return Response(
            {
                'max_step': max_step['step__max'] - 1
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='report/workdiary-time-class')
    def report_workdiary_time_class(self, request):
        query_filter = Q()
        year = self.request.query_params.get('year', None)
        if year is not None:
            query_filter &= Q(started_on__year=year)

        month = self.request.query_params.get('month', None)
        if month is not None:
            query_filter &= Q(started_on__month=month)

        queryset = m.Job.completed_jobs.filter(query_filter)
        page = self.paginate_queryset(queryset)
        serializer = s.JobWorkTimeDurationSerializer(
            page,
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='report/workdiary-weight-class')
    def report_workdiary_weight_class(self, request):
        query_filter = Q()
        year = self.request.query_params.get('year', None)
        if year is not None:
            query_filter &= Q(started_on__year=year)

        month = self.request.query_params.get('month', None)
        if month is not None:
            query_filter &= Q(started_on__month=month)

        plate_num = self.request.query_params.get('vehicle', None)
        if plate_num is not None:
            query_filter &= Q(vehicle__plate_num=plate_num)

        queryset = m.Job.completed_jobs.filter(query_filter)
        page = self.paginate_queryset(queryset)
        serializer = s.JobWorkDiaryWeightClassSerializer(
            page,
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

        # check if the requester belongs to which department
        # if request.user.profile.department.name == '壳牌项目部':
        #     """
        #     this department manage the unloading product by volume
        #     """
        #     instance.weight = request.data.pop('weight', 0)
        # elif request.user.profile.department.name == '油品配送部':
        #     """
        #     this department manage the unloading product by weight
        #     """
        #     instance.weight = request.data.pop('weight', 0)

        instance.weight = request.data.pop('weight', 0)
        instance.save()

        # update order product delivered weight
        order = instance.job_station.job.order
        order_product = order.orderproduct_set.filter(product=instance.product).first()
        order_product.delivered_weight += instance.weight
        order_product.save()

        for image in images:
            image['job_station_product'] = instance.id
            serializer = s.JobStationProductDocumentSerializer(data=image)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        ret = {
            'branch': instance.branch,
            'weight': instance.weight,
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


class OrderPaymentViewSet(viewsets.ModelViewSet):

    queryset = m.OrderPayment.objects.all()
    serializer_class = s.OrderPaymentSerializer

    @action(detail=True, methods=['post'], url_path='update-distance')
    def update_order_payment_distance(self, request, pk=None):
        instance = self.get_object()
        instance.distance = float(request.data.get('distance', 0))
        instance.adjustment = float(request.data.get('adjustment', 0))
        if instance.status == c.ORDER_PAYMENT_STATUS_NO_DISTANCE:
            instance.status = c.ORDER_PAYMENT_STATUS_WAITING_DUIZHANG

        instance.save()
        return Response(
            s.OrderPaymentSerializer(instance).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'], url_path='confirm-duizhang')
    def confirm_duizhang(self, request, pk=None):
        """
        this api will be called from customer app
        """
        instance = self.get_object()
        if instance.status != c.ORDER_PAYMENT_STATUS_WAITING_DUIZHANG:
            return Response(
                {
                    'msg': 'You cannot duizhang because due to its current status'
                }
            )

        if instance.job_station.job.order.invoice_ticket:
            instance.status = c.ORDER_PAYMENT_STATUS_WAITING_TICKET
        else:
            instance.status = c.ORDER_PAYMENT_STATUS_WAITING_PAYMENT_CONFRIM

        instance.save()
        return Response(
            s.OrderPaymentSerializer(instance).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'], url_path='confirm-payment')
    def confirm_order_payment(self, request, pk=None):
        """
        this api will be called from customer app
        """
        instance = self.get_object()
        if instance.status != c.ORDER_PAYMENT_STATUS_WAITING_PAYMENT_CONFRIM:
            return Response(
                {
                    'msg': 'You cannot duizhang because due to its current status'
                }
            )

        instance.status = c.ORDER_PAYMENT_STATUS_COMPLETE
        instance.save()
        return Response(
            s.OrderPaymentSerializer(instance).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, url_path='current-status')
    def get_current_status(self, request, pk=None):
        instance = self.get_object()
        return Response(
            s.OrderPaymentStatusSerializer(instance).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], url_path='update-status')
    def update_order_payment_status(self, request, pk=None):
        instance = self.get_object()
        instance.status = int(request.data.get('status', 0))
        instance.save()
        return Response(
            s.OrderPaymentSerializer(instance).data,
            status=status.HTTP_200_OK
        )


class JobWorkerViewSet(viewsets.ModelViewSet):

    queryset = m.JobWorker.objects.all()

    def destroy(self, request, pk=None):
        job_worker = self.get_object()
        job = job_worker.job
        if job_worker.is_active:
            return Response(
                {
                    'msg': 'cannot delete the active job worker'
                }
            )

        job_worker.delete()
        workers = job.jobworker_set.order_by('assigned_on')
        return Response(
            s.ShortJobWorkerSerializer(workers, many=True).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='report-time')
    def report_time(self, request):
        query_filter = Q(job__progress=c.JOB_PROGRESS_COMPLETE)
        year = request.query_params.get('year', None)
        if year is not None:
            query_filter &= Q(started_on__year=year)

        month = request.query_params.get('month', None)
        if month is not None:
            query_filter &= Q(started_on__month=month)

        worker_type = request.query_params.get('worker_type', None)
        if worker_type is not None:
            query_filter &= Q(worker_type=worker_type)

        queryset = self.queryset.filter(query_filter)

        page = self.paginate_queryset(queryset)
        serializer = s.ReportJobWorkingTimeSerializer(
            page,
            many=True
        )
        return self.get_paginated_response(serializer.data)


class JobWorkerExportViewSet(XLSXFileMixin, viewsets.ReadOnlyModelViewSet):
    """
    工时统计
    """
    queryset = m.JobWorker.objects.filter(job__progress=c.JOB_PROGRESS_COMPLETE)
    serializer_class = s.ReportJobWorkingTimeSerializer
    pagination_class = None
    renderer_classes = (XLSXRenderer, )
    filename = 'export.xlsx'
    body = c.EXCEL_BODY_STYLE

    def get_column_header(self):
        ret = c.EXCEL_HEAD_STYLE
        ret['titles'] = [
            '日期', '名称', '分类', '装货地', '货品', '是否混装', '配送油站数量',
            '装油工时', '质检工时', '卸油工时', '航次所用工时',
        ]
        ret['column_width'] = [30, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
        return ret

    def get_queryset(self):
        queryset = self.queryset
        query_filter = Q()
        year = self.request.query_params.get('year', None)
        if year is not None:
            query_filter &= Q(started_on__year=year)

        month = self.request.query_params.get('month', None)
        if month is not None:
            query_filter &= Q(started_on__month=month)

        worker_type = self.request.query_params.get('worker_type', None)
        if worker_type is not None:
            query_filter &= Q(worker_type=worker_type)

        queryset = self.queryset.filter(query_filter)

        return queryset


class JobWorkDiaryExportViewSet(XLSXFileMixin, viewsets.ReadOnlyModelViewSet):
    """
    业务台账统计
    """
    queryset = m.Job.completed_jobs.all()
    serializer_class = s.JobWorkDiaryReportSerializer
    pagination_class = None
    renderer_classes = (XLSXRenderer, )
    filename = 'export.xlsx'
    body = c.EXCEL_BODY_STYLE

    def get_column_header(self):
        ret = c.EXCEL_HEAD_STYLE
        ret['titles'] = [
            '日期', '车牌', '航次', '路线', '驾驶员', '押运员', '里程数',
            '磅单毛重', '磅单皮重', '磅单净重', '加油数量', '加油费', '油卡余额', '加油类型',
            '路桥费', '鲁通卡', '总费用', '装货地', '货品', '混装', '站数量',
        ]
        ret['column_width'] = [
            30, 20, 10, 60, 20, 20, 20,
            20, 20, 20, 20, 20, 20, 20,
            20, 20, 20, 20, 20, 20, 20,
        ]
        return ret

    def get_queryset(self):
        queryset = self.queryset
        query_filter = Q()
        year = self.request.query_params.get('year', None)
        if year is not None:
            query_filter &= Q(started_on__year=year)

        month = self.request.query_params.get('month', None)
        if month is not None:
            query_filter &= Q(started_on__month=month)

        queryset = self.queryset.filter(query_filter)

        return queryset


class JobWorkTimeDurationViewSet(XLSXFileMixin, viewsets.ReadOnlyModelViewSet):
    """
    装油时间统计
    """
    queryset = m.Job.completed_jobs.all()
    serializer_class = s.JobWorkTimeDurationSerializer
    pagination_class = None
    renderer_classes = (XLSXRenderer, )
    filename = 'export.xlsx'
    body = c.EXCEL_BODY_STYLE
    max_step = 3

    def get_column_header(self):
        ret = c.EXCEL_HEAD_STYLE
        ret['titles'] = [
            '日期', '车牌', '航次', '路线',
            '装货等待时间', '装油时间', '质检等待时间', '质检操作时间',
        ]

        max_step = self.max_step
        while max_step:
            ret['titles'].extend(['卸油等待时间', '卸油时间', '卸仓数量'])
            max_step = max_step - 1

        ret['column_width'] = [
            30, 20, 10, 60,
        ]
        return ret

    def get_queryset(self):
        queryset = self.queryset
        query_filter = Q()
        year = self.request.query_params.get('year', None)
        if year is not None:
            query_filter &= Q(started_on__year=year)

        month = self.request.query_params.get('month', None)
        if month is not None:
            query_filter &= Q(started_on__month=month)

        queryset = self.queryset.filter(query_filter)

        max_step = m.JobStation.objects.filter(job__in=queryset).aggregate(Max('step'))
        self.max_step = max_step['step__max'] - 1   # unlaoding station count
        return queryset


class JobWorkDiaryWeightClassViewSet(XLSXFileMixin, viewsets.ReadOnlyModelViewSet):
    """
    装油时间统计
    """
    queryset = m.Job.completed_jobs.all()
    serializer_class = s.JobWorkDiaryWeightClassSerializer
    pagination_class = None
    renderer_classes = (XLSXRenderer, )
    filename = 'export.xlsx'
    body = c.EXCEL_BODY_STYLE

    def get_column_header(self):
        ret = c.EXCEL_HEAD_STYLE
        ret['titles'] = [
            '车牌', '日期', '实发流量', '实收流量', '差异', '是否需要解释', '原因（±100L)', '损益率（千分之）'
        ]

        ret['column_width'] = [
            20, 30, 10, 10, 10, 10, 10, 10
        ]
        return ret

    def get_queryset(self):
        queryset = self.queryset
        query_filter = Q()
        year = self.request.query_params.get('year', None)
        if year is not None:
            query_filter &= Q(started_on__year=year)

        month = self.request.query_params.get('month', None)
        if month is not None:
            query_filter &= Q(started_on__month=month)

        plate_num = self.request.query_params.get('vehicle', None)
        if plate_num is not None:
            query_filter &= Q(vehicle__plate_num=plate_num)

        queryset = self.queryset.filter(query_filter)

        return queryset
