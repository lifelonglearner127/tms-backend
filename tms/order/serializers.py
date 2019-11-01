# from collections import defaultdict
# from django.db.models import Q
from django.shortcuts import get_object_or_404
# from django.utils import timezone as datetime
from rest_framework import serializers

from . import models as m
from ..core import constants as c
# from ..core.utils import format_datetime

# models
from ..hr.models import CustomerProfile, StaffProfile
from ..info.models import Product
from ..finance.models import FuelBillHistory

# serializers
from ..core.serializers import TMSChoiceField, Base64ImageField
from ..account.serializers import MainUserSerializer
from ..hr.serializers import (
    ShortCustomerProfileSerializer, ShortStaffProfileSerializer,
    ShortProfileNameSerializer
)
from ..finance.serializers import FuelBillHistorySerializer
from ..info.serializers import (
    StationLocationSerializer, ProductNameSerializer, StationContactSerializer,
    StationNameSerializer
)
from ..route.serializers import ShortRouteSerializer, RouteSerializer
from ..vehicle.serializers import ShortVehicleSerializer, ShortVehiclePlateNumSerializer
from .tasks import notify_order_changes


class OrderCartSerializer(serializers.ModelSerializer):

    product = ProductNameSerializer(read_only=True)

    class Meta:
        model = m.OrderCart
        fields = '__all__'

    def create(self, validated_data):
        # validate payload
        # product validation
        product_data = self.context.get('product', None)
        if product_data is None:
            raise serializers.ValidationError({
                'product': 'Product data is missing'
            })

        try:
            product = Product.objects.get(
                id=product_data.get('id', None)
            )
        except Product.DoesNotExist:
            raise serializers.ValidationError({
                'product': 'Such Product does not exist'
            })

        # create cart item
        return m.OrderCart.objects.create(
            product=product,
            **validated_data
        )

    def update(self, instance, validated_data):
        # validate payload
        # product validation
        product_data = self.context.get('product', None)
        if product_data is None:
            raise serializers.ValidationError({
                'product': 'Product data is missing'
            })

        try:
            product = Product.objects.get(
                id=product_data.get('id', None)
            )
        except Product.DoesNotExist:
            raise serializers.ValidationError({
                'product': 'Such Product does not exist'
            })

        instance.product = product

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


class ShortJobSerializer(serializers.ModelSerializer):

    driver = MainUserSerializer()
    escort = MainUserSerializer()
    vehicle = ShortVehicleSerializer()
    route = ShortRouteSerializer()

    class Meta:
        model = m.Job
        fields = (
            'id', 'vehicle', 'driver', 'escort', 'route'
        )


class OrderProductSerializer(serializers.ModelSerializer):
    """
    Serializer for ordred products
    """
    product = ProductNameSerializer(read_only=True)
    weight_measure_unit = TMSChoiceField(
        choices=c.PRODUCT_WEIGHT_MEASURE_UNIT
    )

    class Meta:
        model = m.OrderProduct
        exclude = (
            'order',
        )


class ShortOrderSerializer(serializers.ModelSerializer):
    assignee = ShortProfileNameSerializer(read_only=True)
    customer = ShortCustomerProfileSerializer(read_only=True)
    loading_station = StationNameSerializer(read_only=True)
    quality_station = StationNameSerializer(read_only=True)
    created = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    updated = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )

    class Meta:
        model = m.Order
        fields = (
            'id',
            'assignee',
            'customer',
            'loading_station',
            'quality_station',
            'created',
            'updated',
            'description',
            'tax_rate',
        )


class OrderCustomerAppSerializer(serializers.ModelSerializer):

    status = TMSChoiceField(choices=c.ORDER_STATUS, required=False)
    arrangement_status = TMSChoiceField(
        choices=c.TRUCK_ARRANGEMENT_STATUS, required=False
    )
    loading_station = StationContactSerializer(read_only=True)
    quality_station = StationContactSerializer(read_only=True)
    products = OrderProductSerializer(
        source='orderproduct_set', many=True, read_only=True
    )
    jobs = serializers.SerializerMethodField()

    class Meta:
        model = m.Order
        fields = (
            'id', 'status', 'loading_station', 'quality_station', 'loading_due_time', 'is_same_station',
            'arrangement_status', 'invoice_ticket', 'tax_rate', 'description', 'products', 'jobs'
        )

    def get_jobs(self, instance):
        ret = []
        for job in instance.jobs.all():
            job_item = {}
            job_item['vehicle'] = job.vehicle.plate_num
            job_item['drivers'] = [job.jobworker_set.filter(worker_type=c.WORKER_TYPE_DRIVER).first().worker.name]
            job_item['escorts'] = [job.jobworker_set.filter(worker_type=c.WORKER_TYPE_DRIVER).first().worker.name]
            job_item['details'] = []
            for job_station in job.jobstation_set.all():
                for ret_station in job_item['details']:
                    if ret_station['station']['id'] == job_station.station.id:
                        for jobstationproduct in job_station.jobstationproduct_set.all():
                            for product in ret_station['products']:
                                if product['product']['id'] == jobstationproduct.product.id:
                                    product['weight'] += jobstationproduct.mission_weight
                                    break
                            else:
                                ret_station['products'].append({
                                    'product': ProductNameSerializer(jobstationproduct.product).data,
                                    'weight': jobstationproduct.mission_weight
                                })
                        break
                else:
                    item = {}
                    item['station'] = StationContactSerializer(job_station.station).data
                    item['products'] = []
                    for jobstationproduct in job_station.jobstationproduct_set.all():
                        for product in item['products']:
                            if product['product']['id'] == jobstationproduct.product.id:
                                product['weight'] += jobstationproduct.mission_weight
                                break

                        else:
                            item['products'].append({
                                'product': ProductNameSerializer(jobstationproduct.product).data,
                                'due_time': jobstationproduct.due_time,
                                'weight': jobstationproduct.mission_weight
                            })

                    job_item['details'].append(item)

        # if len(ret) > 0:
        #     ret[0]['remaining'] = []
        #     for product in instance.orderproduct_set.all():
        #         for ret_product in ret[0]['products']:
        #             if ret_product['product']['id'] == product.product.id and ret_product['weight'] < product.weight:
        #                 ret[0]['remaining'].append({
        #                     'product': ProductNameSerializer(product.product).data,
        #                     'weight': product.weight - ret_product['weight']
        #                 })

            ret.append(job_item)
        return ret


class OrderSerializer(serializers.ModelSerializer):
    """
    order model serializer
    """
    assignee = ShortStaffProfileSerializer(read_only=True)
    customer = ShortCustomerProfileSerializer(read_only=True)
    loading_station = StationLocationSerializer(read_only=True)
    quality_station = StationLocationSerializer(read_only=True)
    order_source = TMSChoiceField(choices=c.ORDER_SOURCE, required=False)
    status = TMSChoiceField(choices=c.ORDER_STATUS, required=False)
    arrangement_status = TMSChoiceField(
        choices=c.TRUCK_ARRANGEMENT_STATUS, required=False
    )
    products = OrderProductSerializer(
        source='orderproduct_set', many=True, read_only=True
    )
    created = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    updated = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )

    class Meta:
        model = m.Order
        fields = '__all__'

    def create(self, validated_data):
        """
        Request format
        {
            alias: alias,
            assignee: { id: '', name: '' },
            customer: { id: '', name: '' },
            loading_station: { id: '', name: '' },
            quality_station: { id: '', name: '' },
            products: [
                product: { id: '', ... },
                weight: 0
            ]
        }
        """
        # check if order products exists in request
        order_products_data = self.context.pop('products', None)
        if order_products_data is None:
            raise serializers.ValidationError({
                'products': 'Order Product data is missing'
            })

        # check if loading station exists
        loading_station_data = self.context.pop('loading_station', None)
        if loading_station_data is None:
            raise serializers.ValidationError({
                'loading_station': 'Loading station data is missing'
            })

        loading_station = get_object_or_404(
            m.Station,
            id=loading_station_data.get('id'),
            station_type=c.STATION_TYPE_LOADING_STATION
        )

        # check if loading station exists
        quality_station_data = self.context.pop('quality_station', None)
        if quality_station_data is None:
            raise serializers.ValidationError({
                'quality_station': 'Quality station data is missing'
            })

        quality_station = get_object_or_404(
            m.Station,
            id=quality_station_data.get('id'),
            station_type=c.STATION_TYPE_QUALITY_STATION
        )

        # save models
        order = m.Order.objects.create(
            loading_station=loading_station,
            quality_station=quality_station,
            **validated_data
        )

        for order_product_data in order_products_data:
            product_data = order_product_data.pop('product', None)
            product = get_object_or_404(
                m.Product, id=product_data.get('id', None)
            )

            if 'weight_measure_unit' in order_product_data:
                order_product_data['weight_measure_unit'] =\
                    order_product_data['weight_measure_unit']['value']

            m.OrderProduct.objects.create(
                order=order, product=product, **order_product_data
            )

        notify_order_changes.apply_async(
            args=[{
                'order': order.id,
                'customer_user_id': order.customer.user.id
            }]
        )
        return order

    def update(self, instance, validated_data):
        """
        Request format
        {
            alias: alias,
            assignee: { id: '', name: '' },
            customer: { id: '', name: '' },
            products: [
                product: { id: '', ... },
                weight: 0
            ]
        }
        1. Validate the data
        2. save models
        """
        # check if order products exists in request
        order_products_data = self.context.get('products', None)
        if order_products_data is None:
            raise serializers.ValidationError({
                'products': 'Order Product data is missing'
            })

        # check if loading station exists
        loading_station_data = self.context.pop('loading_station', None)
        if loading_station_data is None:
            raise serializers.ValidationError({
                'loading_station': 'Loading station data is missing'
            })

        loading_station = get_object_or_404(
            m.Station,
            id=loading_station_data.get('id'),
            station_type=c.STATION_TYPE_LOADING_STATION
        )

        # check if loading station exists
        quality_station_data = self.context.pop('quality_station', None)
        if quality_station_data is None:
            raise serializers.ValidationError({
                'quality_station': 'Quality station data is missing'
            })

        quality_station = get_object_or_404(
            m.Station,
            id=quality_station_data.get('id'),
            station_type=c.STATION_TYPE_QUALITY_STATION
        )

        instance.loading_station = loading_station
        instance.quality_station = quality_station

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        old_products = set(
            instance.orderproduct_set.values_list('id', flat=True)
        )

        new_products = set()

        # save models
        for order_product_data in order_products_data:
            product_data = order_product_data.pop('product', None)
            product = get_object_or_404(
                m.Product,
                id=product_data.get('id', None)
            )

            if 'weight_measure_unit' in order_product_data:
                order_product_data['weight_measure_unit'] =\
                    order_product_data['weight_measure_unit']['value']

            order_product_id = order_product_data.get('id', None)
            new_products.add(order_product_id)
            if order_product_id not in old_products:
                order_product = m.OrderProduct.objects.create(
                    order=instance, product=product, **order_product_data
                )
            else:
                order_product = get_object_or_404(
                    m.OrderProduct,
                    id=order_product_id
                )

                for (key, value) in order_product_data.items():
                    setattr(order_product, key, value)
                order_product.save()

        m.OrderProduct.objects.filter(
            order=instance,
            id__in=old_products.difference(new_products)
        ).delete()

        return instance

    def to_internal_value(self, data):
        ret = data
        if 'assignee' in data:
            ret['assignee'] = get_object_or_404(StaffProfile, id=data['assignee']['id'])
        ret['customer'] = get_object_or_404(
            CustomerProfile, id=data['customer']['id']
        )
        return ret


class JobMileageField(serializers.Field):

    def to_representation(self, instance):
        return {
            'total_mileage': instance.total_mileage,
            'highway_mileage': instance.highway_mileage,
            'normalway_mileage': instance.normalway_mileage,
            'empty_mileage': instance.empty_mileage,
            'heavy_mileage':  instance.heavy_mileage
        }


class JobDurationField(serializers.Field):

    def to_representation(self, instance):
        durations = []
        if instance.started_on is None:
            return durations

        time_list = [instance.started_on]
        job_stations = instance.jobstation_set.all()
        for job_station in job_stations:
            if job_station.arrived_station_on is None:
                break
            time_list.append(job_station.arrived_station_on)

            if job_station.started_working_on is None:
                break
            time_list.append(job_station.started_working_on)

            if job_station.finished_working_on is None:
                break
            time_list.append(job_station.finished_working_on)

            if job_station.departure_station_on is None:
                break
            time_list.append(job_station.departure_station_on)

        if instance.finished_on is not None:
            time_list.append(instance.finished_on)

        # station_duration = []
        # for i in range(len(time_list) - 1):
        #     if i % 4 == 0:
        #         station_duration = []
        #     elif i % 4 == 3:
        #         durations.append(station_duration)

        #     station_duration.append(
        #         round(
        #             (time_list[i + 1] - time_list[i]).total_seconds() / 60
        #         )
        #     )

        for i in range(len(time_list) - 1):
            durations.append(
                round(
                    (time_list[i + 1] - time_list[i]).total_seconds() / 60
                )
            )

        return durations


class QualityCheckSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.QualityCheck
        exclude = (
            'job',
        )


class ShortJobStationProductSerializer(serializers.ModelSerializer):

    product = ProductNameSerializer(read_only=True)

    class Meta:
        model = m.JobStationProduct
        fields = (
            'id', 'product', 'branch', 'mission_weight', 'volume'
        )


class JobStationLoadingProductSerializer(serializers.ModelSerializer):

    product = ProductNameSerializer()

    class Meta:
        model = m.JobStationProduct
        fields = (
            'id', 'product', 'mission_weight'
        )


class JobStationUnloadingProductSerializer(serializers.ModelSerializer):

    product = ProductNameSerializer()

    class Meta:
        model = m.JobStationProduct
        fields = (
            'id', 'product', 'volume'
        )


class JobStationProductSerializer(serializers.ModelSerializer):

    product = ProductNameSerializer(read_only=True)

    class Meta:
        model = m.JobStationProduct
        exclude = (
            'job_station',
        )


class ShortJobStationProductDocumentSerializer(serializers.ModelSerializer):

    document = Base64ImageField()

    class Meta:
        model = m.JobStationProductDocument
        exclude = (
            'job_station_product',
        )


class JobStationProductDocumentSerializer(serializers.ModelSerializer):

    document = Base64ImageField()

    class Meta:
        model = m.JobStationProductDocument
        fields = '__all__'


class ShortJobStationSerializer(serializers.ModelSerializer):

    station = StationContactSerializer()
    products = ShortJobStationProductSerializer(
        source='jobstationproduct_set', many=True, read_only=True
    )
    due_time = serializers.SerializerMethodField()

    class Meta:
        model = m.JobStation
        fields = (
            'id', 'station', 'products', 'due_time',
        )

    def get_due_time(self, instance):
        if instance.step > 1:
            due_time = instance.due_time
        else:
            due_time = instance.job.order.loading_due_time

        return due_time.strftime('%Y-%m-%d')


class JobStationTimeSerializer(serializers.ModelSerializer):

    arrived_station_on = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    started_working_on = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    finished_working_on = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    departure_station_on = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = m.JobStation
        fields = (
            'arrived_station_on',
            'started_working_on',
            'finished_working_on',
            'departure_station_on',
        )


class JobStationSerializer(serializers.ModelSerializer):

    products = JobStationProductSerializer(
        source='jobstationproduct_set', many=True, read_only=True
    )

    class Meta:
        model = m.JobStation
        exclude = (
            'job', 'step'
        )


class JobWorkerSerializer(serializers.ModelSerializer):

    worker = MainUserSerializer(read_only=True)

    class Meta:
        model = m.JobWorker
        exclude = (
            'job',
        )


class JobAdminSerializer(serializers.ModelSerializer):

    vehicle = ShortVehicleSerializer()
    driver = serializers.SerializerMethodField()
    escort = serializers.SerializerMethodField()
    routes = serializers.SerializerMethodField()
    rest_place = StationNameSerializer()
    branches = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = m.Job
        fields = (
            'id', 'vehicle', 'driver', 'escort', 'rest_place', 'routes', 'branches', 'progress'
        )

    def get_driver(self, instance):
        job_driver = m.JobWorker.drivers.filter(job=instance).first()
        return MainUserSerializer(job_driver.worker).data

    def get_escort(self, instance):
        job_escort = m.JobWorker.escorts.filter(job=instance).first()
        return MainUserSerializer(job_escort.worker).data

    def get_routes(self, instance):
        routes = m.Route.objects.filter(id__in=instance.routes)
        routes = dict([(route.id, route) for route in routes])
        return RouteSerializer(
            [routes[id] for id in instance.routes],
            many=True
        ).data

    def get_branches(self, instance):
        branches = []
        branch_ids = []
        for job_station in instance.jobstation_set.all()[2:]:
            for job_station_product in job_station.jobstationproduct_set.all():
                for branch in branches:
                    if branch['branch']['id'] == job_station_product.branch:
                        branch['mission_weight'] += job_station_product.mission_weight
                        branch['unloading_stations'].append({
                            'unloading_station': StationLocationSerializer(job_station.station).data,
                            'due_time': job_station_product.due_time,
                            'mission_weight': job_station_product.mission_weight
                        })
                        break
                else:
                    branch_ids.append(job_station_product.branch)
                    branches.append({
                        'is_checked': True,
                        'branch': {'id': job_station_product.branch},
                        'product': ProductNameSerializer(job_station_product.product).data,
                        'mission_weight': job_station_product.mission_weight,
                        'unloading_stations': [{
                            'unloading_station': StationLocationSerializer(job_station.station).data,
                            'due_time': job_station_product.due_time,
                            'transport_unit_price': job_station.transport_unit_price,
                            'mission_weight': job_station_product.mission_weight
                        }]
                    })

        empty_branches = [branch_id for branch_id in range(0, 3) if branch_id not in branch_ids]
        for empty_branch in empty_branches:
            branches.append({
                'is_checked': False,
                'branch': {'id': empty_branch},
                'product': None,
                'mission_weight': 0,
                'unloading_stations': [{
                    'unloading_station': None,
                    'due_time': '',
                    'mission_weight': 0
                }]
            })
        branches.sort(key=lambda branch: branch['branch']['id'])
        return branches

    def get_progress(self, instance):
        if instance.progress >= 10:
            if (instance.progress - 10) % 4 == 0:
                progress = 10
            elif (instance.progress - 10) % 4 == 1:
                progress = 11
            elif (instance.progress - 10) % 4 == 2:
                progress = 12
            elif (instance.progress - 10) % 4 == 3:
                progress = 13
        else:
            progress = instance.progress

        return c.JOB_PROGRESS.get(progress, '无任务')


class JobUnloadingStationProductSerializer(serializers.Field):

    def to_representation(self, instance):
        return {
            'total_mileage': instance.total_mileage,
            'highway_mileage': instance.highway_mileage,
            'normalway_mileage': instance.normalway_mileage,
            'empty_mileage': instance.empty_mileage,
            'heavy_mileage':  instance.heavy_mileage
        }


class JobSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Job
        fields = '__all__'


class JobDoneSerializer(serializers.ModelSerializer):
    """
    this serializer is used in workdiary
    """
    order = ShortOrderSerializer()
    vehicle = ShortVehiclePlateNumSerializer()
    associated_drivers = serializers.SerializerMethodField()
    associated_escorts = serializers.SerializerMethodField()
    branches = serializers.SerializerMethodField()
    routes = serializers.SerializerMethodField()
    stations = serializers.SerializerMethodField()
    costs = serializers.SerializerMethodField()
    mileage = JobMileageField(source='*')
    durations = JobDurationField(source='*')
    started_on = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)
    finished_on = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)

    class Meta:
        model = m.Job
        fields = (
            'id', 'order', 'vehicle', 'associated_drivers', 'associated_escorts', 'branches',
            'routes', 'stations', 'costs', 'mileage', 'durations', 'started_on', 'finished_on',
            'is_paid', 'freight_payment_to_driver',
        )

    def get_associated_drivers(self, instance):
        return JobWorkerSerializer(
            instance.jobworker_set.filter(worker_type=c.WORKER_TYPE_DRIVER),
            many=True
        ).data

    def get_associated_escorts(self, instance):
        return JobWorkerSerializer(
            instance.jobworker_set.filter(worker_type=c.WORKER_TYPE_ESCORT),
            many=True
        ).data

    def get_routes(self, instance):
        routes = m.Route.objects.filter(id__in=instance.routes)
        routes = dict([(route.id, route) for route in routes])
        return RouteSerializer(
            [routes[id] for id in instance.routes],
            many=True
        ).data

    def get_branches(self, instance):
        branches = []
        for job_station in instance.jobstation_set.all()[2:]:
            for job_station_product in job_station.jobstationproduct_set.all():
                for branch in branches:
                    if branch['branch'] == job_station_product.branch:
                        branch['mission_weight'] += job_station_product.mission_weight
                        branch['unloading_stations'].append({
                            'unloading_station': StationNameSerializer(job_station.station).data,
                            'mission_weight': job_station_product.mission_weight
                        })
                        break
                else:
                    order_product = instance.order.orderproduct_set.filter(product=job_station_product.product).first()

                    branches.append({
                        'branch': job_station_product.branch,
                        'product': ProductNameSerializer(job_station_product.product).data,
                        'mission_weight': job_station_product.mission_weight,
                        'weight_measure_unit': order_product.get_weight_measure_unit_display(),
                        'unloading_stations': [{
                            'unloading_station': StationNameSerializer(job_station.station).data,
                            'mission_weight': job_station_product.mission_weight
                        }]
                    })

        return branches

    def get_stations(self, instance):
        job_stations = instance.jobstation_set.all()
        ret = {
            'loading_station': {
                'time': JobStationTimeSerializer(job_stations[0]).data,
                'station': StationNameSerializer(job_stations[0].station).data,
                'loading_checks': []
            },
            'quality_station': {
                'time': JobStationTimeSerializer(job_stations[1]).data,
                'station': StationNameSerializer(job_stations[1].station).data,
                'branches': []
            },
            'unloading_stations': []
        }

        # this code is really redundant, I know about it, but this is the kind request from app dev
        loading_checks = []
        for product in instance.products:
            try:
                loading_check = m.LoadingStationProductCheck.objects.get(job=instance, product=product)
                loading_checks.append(loading_check)
            except m.LoadingStationProductCheck.DoesNotExist:
                loading_checks.append({
                    'job': instance,
                    'product': product,
                    'weight': 0
                })

        ret['loading_station']['loading_checks'] = LoadingStationProductCheckSerializer(
            loading_checks, context={'request': self.context.get('request')}, many=True
        ).data

        # this is the original code of above app dev request.
        # ret['loading_station']['loading_checks'] = LoadingStationProductCheckSerializer(
        #     instance.loading_checks.all(), context={'request': self.context.get('request')}, many=True
        # ).data

        quality_station = job_stations[1]
        for product in quality_station.jobstationproduct_set.all():
            quality_check = instance.quality_checks.filter(branch=product.branch).first()

            # actually there is no need to send empty quality check, but this is the kind request from app dev
            if quality_check is not None:
                density = quality_check.density
                additive = quality_check.additive
            else:
                density = 0
                additive = 0

            ret['quality_station']['branches'].append({
                'branch': product.branch,
                'product': ProductNameSerializer(product.product).data,
                'weight': product.weight,
                'due_time': product.due_time,
                'density': density,
                'additive': additive,
                'volume': product.volume,
                'man_hole': product.man_hole,
                'branch_hole': product.branch_hole,
                'images': ShortJobStationProductDocumentSerializer(
                    product.images.all(), context={'request': self.context.get('request')}, many=True
                ).data
            })

        for job_station in job_stations[2:]:
            station_payload = {
                'id': job_station.id,
                'station': StationNameSerializer(job_station.station).data,
                'time': JobStationTimeSerializer(job_station).data,
                'branches': []
            }

            for product in job_station.jobstationproduct_set.all():
                station_payload['branches'].append({
                    'id': product.id,
                    'branch': product.branch,
                    'product': ProductNameSerializer(product.product).data,
                    'due_time': product.due_time,
                    'volume': product.volume,
                    'man_hole': product.man_hole,
                    'branch_hole': product.branch_hole,
                    'images': ShortJobStationProductDocumentSerializer(
                        product.images.all(), context={'request': self.context.get('request')}, many=True
                    ).data
                })

            ret['unloading_stations'].append(station_payload)
        return ret

    def get_costs(self, instance):
        ret = {
            'fuel': {}
        }
        vehicle = instance.vehicle
        previous_job = vehicle.jobs.exclude(id=instance.id).filter(progress=c.JOB_PROGRESS_COMPLETE).first()
        if previous_job is not None and previous_job.finished_on is not None:
            bill_history = FuelBillHistory.objects.filter(
                created_on__range=(previous_job.finished_on, instance.finished_on)
            )
        else:
            bill_history = FuelBillHistory.objects.filter(
                created_on__lte=instance.finished_on
            )

        ret['fuel'] = FuelBillHistorySerializer(
            bill_history, context={'request': self.context.get('request')}, many=True
        ).data
        return ret


class JobFutureSerializer(serializers.ModelSerializer):
    """
    Serializer for future job for driver app
    """
    plate_num = serializers.CharField(source='vehicle.plate_num')
    routes = serializers.SerializerMethodField()
    total_distance = serializers.SerializerMethodField()
    driver = serializers.SerializerMethodField()
    escort = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()
    stations = ShortJobStationSerializer(
        source='jobstation_set', many=True, read_only=True
    )
    progress_bar = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    order_description = serializers.CharField(source='order.description')

    class Meta:
        model = m.Job
        fields = (
            'id',
            'plate_num',
            'total_distance',
            'routes',
            'driver',
            'escort',
            'products',
            'stations',
            'progress_bar',
            'progress',
            'order_description',
        )

    def get_total_distance(self, instance):
        total_distance = 0
        routes = m.Route.objects.filter(id__in=instance.routes)
        for route in routes:
            total_distance += route.distance
        return round(total_distance, 1)

    def get_routes(self, instance):
        routes = m.Route.objects.filter(id__in=instance.routes)
        routes = dict([(route.id, route) for route in routes])
        return RouteSerializer(
            [routes[id] for id in instance.routes],
            many=True
        ).data

    def get_driver(self, instance):
        return instance.jobworker_set.filter(worker_type=c.WORKER_TYPE_DRIVER).first().worker.name

    def get_escort(self, instance):
        return instance.jobworker_set.filter(worker_type=c.WORKER_TYPE_ESCORT).first().worker.name

    def get_products(self, instance):
        ret = []
        loading_station = instance.jobstation_set.all()[0]
        for product in loading_station.jobstationproduct_set.all():
            for ret_product in ret:
                if ret_product['product']['id'] == product.product.id:
                    ret_product['mission_weight'] += product.mission_weight
                    break
            else:
                ret.append({
                    'product': ProductNameSerializer(product.product).data,
                    'mission_weight': product.mission_weight
                })

        return ret

    def get_progress_bar(self, instance):
        ret = []
        ret.append({'title': '出发'})

        stations = instance.stations.all()
        ret.append({'title': '赶往装货地:' + stations[0].name})
        ret.append({'title': '到达等待装货'})
        ret.append({'title': '开始装货'})
        ret.append({'title': '录入装货数量'})

        ret.append({'title': '赶往质检地:' + stations[1].name})
        ret.append({'title': '到达等待质检'})
        ret.append({'title': '开始质检'})
        ret.append({'title': '录入质检量'})

        for station in stations[2:]:
            ret.append({'title': '赶往卸货地:' + station.name})
            ret.append({'title': '到达等待卸货'})
            ret.append({'title': '开始卸货'})
            ret.append({'title': '录入卸货数量'})

        progress = 1
        for item in ret:
            item['progress'] = progress
            item['active'] = progress == instance.progress
            progress = progress + 1

        ret.append({
            'title': '完成',
            'progress': c.JOB_PROGRESS_COMPLETE,
            'active': instance.progress == c.JOB_PROGRESS_COMPLETE
        })

        return ret

    def get_progress(self, instance):
        current_progress = instance.progress
        if current_progress == c.JOB_PROGRESS_NOT_STARTED:
            last_progress_finished_on = None
        elif current_progress == c.JOB_PROGRESS_TO_LOADING_STATION:
            last_progress_finished_on = instance.started_on
        else:
            progress_from_start =\
                current_progress - c.JOB_PROGRESS_ARRIVED_AT_LOADING_STATION
            station_step = int(progress_from_start / 4)
            sub_progress = progress_from_start % 4

            station = instance.jobstation_set.get(step=station_step)
            if sub_progress == 0:
                last_progress_finished_on = station.arrived_station_on
            elif sub_progress == 1:
                last_progress_finished_on = station.started_working_on
            elif sub_progress == 2:
                last_progress_finished_on = station.finished_working_on
            elif sub_progress == 3:
                last_progress_finished_on = station.departure_station_on

        return {
            'progress': current_progress,
            'last_progress_finished_on': last_progress_finished_on
        }


class JobCurrentSerializer(JobFutureSerializer):
    """
    Serializer for current job for driver app
    """
    pass


class BillSubCategoyChoiceField(serializers.Field):

    def to_representation(self, instance):
        if instance.sub_category is None:
            return None

        sub_categories = None
        if instance.category == c.BILL_FROM_OIL_STATION:
            sub_categories = c.OIL_BILL_SUB_CATEGORY
        elif instance.category == c.BILL_FROM_TRAFFIC:
            sub_categories = c.TRAFFIC_BILL_SUB_CATEGORY
        elif instance.category == c.BILL_FROM_OTHER:
            sub_categories = c.OTHER_BILL_SUB_CATEGORY

        if sub_categories is None:
            return None

        choices = dict((x, y) for x, y in sub_categories)
        ret = {
            'value': instance.sub_category,
            'text': choices[instance.sub_category]
        }
        return ret

    def to_internal_value(self, data):
        return {
            'sub_category': data['value']
        }


class BillDetailCategoyChoiceField(serializers.Field):

    def to_representation(self, instance):
        if (
            instance.category != c.BILL_FROM_OTHER or
            instance.sub_category != c.TRAFFIC_VIOLATION_BILL
        ):
            return None

        choices = dict(
            (x, y) for x, y in c.TRAFFIC_VIOLATION_DETAIL_CATEGORY
        )
        ret = {
            'value': instance.detail_category,
            'text': choices[instance.detail_category]
        }
        return ret

    def to_internal_value(self, data):
        return {
            'detail_category': data['value']
        }


class DriverJobReportSerializer(serializers.ModelSerializer):

    year = serializers.CharField(source='month.year')
    month = serializers.CharField(source='month.month')

    class Meta:
        model = m.JobReport
        fields = (
            'year', 'month', 'total_mileage', 'empty_mileage',
            'heavy_mileage', 'highway_mileage', 'normalway_mileage'
        )


class VehicleStatusOrderSerializer(serializers.Serializer):

    id = serializers.CharField()
    plate_num = serializers.CharField()
    # progress = serializers.CharField()
    # client_name = serializers.CharField()
    distance = serializers.FloatField()
    duration = serializers.FloatField()
    total_load = serializers.CharField()
    branch1 = serializers.CharField()
    branch2 = serializers.CharField()
    branch3 = serializers.CharField()
    g7_error = serializers.BooleanField()


class JobByVehicleSerializer(serializers.ModelSerializer):
    """
    Serialize the query result of jobs by plate number and time period
    Used for truck playback response
    """
    alias = serializers.CharField(source='order.alias')
    products = ProductNameSerializer(source='order.products', many=True)
    driver = MainUserSerializer(read_only=True)
    escort = MainUserSerializer(read_only=True)

    class Meta:
        model = m.Job
        fields = (
            'id', 'alias', 'products', 'driver', 'escort', 'started_on',
            'finished_on'
        )


class ShortLoadingStationDocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.LoadingStationDocument
        exclude = ('loading_station', )


class LoadingStationDocumentSerializer(serializers.ModelSerializer):

    document = Base64ImageField()

    class Meta:
        model = m.LoadingStationDocument
        fields = '__all__'


class LoadingStationProductCheckSerializer(serializers.ModelSerializer):

    product = ProductNameSerializer(read_only=True)
    images = serializers.SerializerMethodField()
    created = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )

    class Meta:
        model = m.LoadingStationProductCheck
        exclude = (
            'job',
        )

    def get_images(self, instance):
        # following 3 line checks are essentially not required, it is the kind request from app developer
        if type(instance) is dict:
            images = []
        else:
            images = instance.images.all()

        return ShortLoadingStationDocumentSerializer(
            images,
            context={'request': self.context.get('request')},
            many=True
        ).data


class CustomerAppOrderReportSerializer(serializers.ModelSerializer):

    year = serializers.CharField(source='month.year')
    month = serializers.CharField(source='month.month')

    class Meta:
        model = m.OrderReport
        fields = (
            'year', 'month', 'orders', 'weights'
        )


class OrderReportSerializer(serializers.ModelSerializer):

    year = serializers.CharField(source='month.year')
    month = serializers.CharField(source='month.month')

    class Meta:
        model = m.OrderReport
        fields = '__all__'


class OrderPaymentSerializer(serializers.ModelSerializer):

    job_started_on = serializers.DateTimeField(
        format='%Y-%m-%d', source='job_station.job.started_on'
    )
    vehicle = ShortVehiclePlateNumSerializer(source='job_station.job.vehicle')
    invoice_ticket = serializers.BooleanField(source='job_station.job.order.invoice_ticket', read_only=True)
    customer = serializers.CharField(source='job_station.job.order.customer.name', read_only=True)
    loading_station = StationNameSerializer(source='job_station.job.order.loading_station', read_only=True)
    unloading_station = StationNameSerializer(source='job_station.station', read_only=True)
    transport_unit_price = serializers.FloatField(source='job_station.transport_unit_price', read_only=True)
    status = TMSChoiceField(choices=c.ORDER_PAYMENT_STATUS)
    loading_products = serializers.SerializerMethodField()
    unloading_products = serializers.SerializerMethodField()

    class Meta:
        model = m.OrderPayment
        fields = (
            'id',
            'job_started_on',
            'vehicle',
            'distance',
            'adjustment',
            'status',
            'customer',
            'invoice_ticket',
            'loading_station',
            'unloading_station',
            'transport_unit_price',
            'loading_products',
            'unloading_products',
            'total_price',
        )

    def get_loading_products(self, instance):
        return JobStationLoadingProductSerializer(
            instance.job_station.jobstationproduct_set.all(), many=True
        ).data

    def get_unloading_products(self, instance):
        return JobStationUnloadingProductSerializer(
            instance.job_station.jobstationproduct_set.all(), many=True
        ).data


class OrderPaymentStatusSerializer(serializers.ModelSerializer):

    status_option = serializers.SerializerMethodField()
    status = TMSChoiceField(choices=c.ORDER_PAYMENT_STATUS)

    class Meta:
        model = m.OrderPayment
        fields = (
            'id',
            'status',
            'status_option',
        )

    def get_status_option(self, instance):
        ret = [
            {
                'value': c.ORDER_PAYMENT_STATUS_WAITING_DUIZHANG,
                'text': '待对账'
            },
            {
                'value': c.ORDER_PAYMENT_STATUS_COMPLETE,
                'text': '结算'
            }
        ]
        if instance.job_station.job.order.invoice_ticket:
            ret.insert(1, {
                'value': c.ORDER_PAYMENT_STATUS_WAITING_PAYMENT_CONFRIM,
                'text': '开票后, 待结算'
            })
        return ret


class ReportJobWorkingTimeSerializer(serializers.ModelSerializer):
    """
    工时统计
    """
    started_on = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)
    worker = serializers.CharField(source='worker.name')
    worker_type = serializers.CharField(source='get_worker_type_display')
    loading_station = serializers.CharField(source='job.order.loading_station.name')
    products = serializers.SerializerMethodField()
    is_multiple_products = serializers.SerializerMethodField()
    unloading_station_count = serializers.SerializerMethodField()
    loading_time_duration = serializers.FloatField(source='job.loading_time_duration')
    quality_time_duration = serializers.FloatField(source='job.quality_time_duration')
    unloading_time_duration = serializers.FloatField(source='job.unloading_time_duration')
    total_time_duration = serializers.FloatField(source='job.total_time_duration')

    class Meta:
        model = m.JobWorker
        fields = (
            'started_on',
            'worker',
            'worker_type',
            'loading_station',
            'products',
            'is_multiple_products',
            'unloading_station_count',
            'loading_time_duration',
            'quality_time_duration',
            'unloading_time_duration',
            'total_time_duration',
        )

    def get_products(self, instance):
        products = instance.job.products.values_list('name', flat=True)
        return ', '.join(products)

    def get_is_multiple_products(self, instance):
        loading_station = instance.job.jobstation_set.first()
        return '是' if len(loading_station.products.values_list('name', flat=True)) > 1 else '不'

    def get_unloading_station_count(self, instance):
        return instance.job.stations.count() - 2


class JobWorkDiaryReportSerializer(serializers.ModelSerializer):
    """
    业务台账统计
    """
    started_on = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)
    vehicle = serializers.CharField(source='vehicle.plate_num')
    loop = serializers.SerializerMethodField()
    line = serializers.SerializerMethodField()
    drivers = serializers.SerializerMethodField()
    escorts = serializers.SerializerMethodField()
    total_weight = serializers.SerializerMethodField()
    truck_weight = serializers.FloatField(source='vehicle.total_load')
    oil_weight = serializers.SerializerMethodField()
    oil_price = serializers.SerializerMethodField()
    oil_card_balance = serializers.SerializerMethodField()
    oil_payment_type = serializers.SerializerMethodField()
    toll = serializers.SerializerMethodField()
    etc_card_balance = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    loading_station = serializers.CharField(source='order.loading_station.name')
    products = serializers.SerializerMethodField()
    is_multiple_products = serializers.SerializerMethodField()
    unloading_station_count = serializers.SerializerMethodField()

    class Meta:
        model = m.Job
        fields = (
            'started_on',
            'vehicle',
            'loop',
            'line',
            'drivers',
            'escorts',
            'total_mileage',
            'total_weight',
            'truck_weight',
            'total_delivered_weight',
            'oil_weight',
            'oil_price',
            'oil_card_balance',
            'oil_payment_type',
            'toll',
            'etc_card_balance',
            'total_price',
            'loading_station',
            'products',
            'is_multiple_products',
            'unloading_station_count',
        )

    def get_loop(self, instance):
        return 1

    def get_line(self, instance):
        line = [station.station.name for station in instance.jobstation_set.all()]
        return ' -> '.join(line)

    def get_drivers(self, instance):
        names = [worker.worker.name for worker in instance.jobworker_set.filter(worker_type=c.WORKER_TYPE_DRIVER)]
        return ', '.join(names)

    def get_escorts(self, instance):
        names = [worker.worker.name for worker in instance.jobworker_set.filter(worker_type=c.WORKER_TYPE_ESCORT)]
        return ', '.join(names)

    def get_total_weight(self, instance):
        return instance.vehicle.total_load + instance.total_delivered_weight

    def get_oil_weight(self, instance):
        pass

    def get_oil_price(self, instance):
        pass

    def get_oil_card_balance(self, instance):
        pass

    def get_oil_payment_type(self, instance):
        return '壳牌'

    def get_toll(self, instance):
        pass

    def get_etc_card_balance(self, instance):
        pass

    def get_total_price(self, instance):
        pass

    def get_products(self, instance):
        products = instance.products.values_list('name', flat=True)
        return ', '.join(products)

    def get_is_multiple_products(self, instance):
        loading_station = instance.jobstation_set.first()
        return '是' if len(loading_station.products.values_list('name', flat=True)) > 1 else '不'

    def get_unloading_station_count(self, instance):
        return instance.stations.count() - 2


class JobWorkTimeDurationSerializer(serializers.ModelSerializer):

    started_on = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)
    vehicle = serializers.CharField(source='vehicle.plate_num')
    loop = serializers.SerializerMethodField()
    line = serializers.SerializerMethodField()
    unloading_stations = serializers.SerializerMethodField()

    class Meta:
        model = m.Job
        fields = (
            'started_on',
            'vehicle',
            'loop',
            'line',
            'waiting_at_loading_station_time_duration',
            'loading_time_duration',
            'waiting_at_quality_station_time_duration',
            'quality_time_duration',
            'unloading_stations'
        )

    def get_loop(self, instance):
        return 1

    def get_line(self, instance):
        line = [station.station.name for station in instance.jobstation_set.all()]
        return ' -> '.join(line)

    def get_unloading_stations(self, instance):
        ret = []
        for station in instance.jobstation_set.all()[2:]:
            tmp_ret = {
                'waiting_time_duration': 0,
                'working_time_duration': 0,
                'weight': 0
            }
            if station.started_working_on is not None and station.arrived_station_on is not None:
                duration = (station.started_working_on - station.arrived_station_on).total_seconds()
                tmp_ret['waiting_time_duration'] = round(duration / 3600, 1)

            if station.started_working_on is not None and station.finished_working_on is not None:
                duration = (station.finished_working_on - station.started_working_on).total_seconds()
                tmp_ret['working_time_duration'] = round(duration / 3600, 1)

            for product in station.jobstationproduct_set.all():
                tmp_ret['weight'] += product.mission_weight
            ret.append(tmp_ret)
        return ret

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        unloading_stations = ret.pop('unloading_stations')
        for index, unloading_station in enumerate(unloading_stations):
            ret['unloading_station' + str(index) + 'waiting_time_duration'] =\
                unloading_station['waiting_time_duration']

            ret['unloading_station' + str(index) + 'working_time_duration'] =\
                unloading_station['working_time_duration']

            ret['unloading_station' + str(index) + 'weight'] =\
                unloading_station['weight']

        return ret


class JobWorkDiaryWeightClassSerializer(serializers.ModelSerializer):

    started_on = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)
    vehicle = serializers.CharField(source='vehicle.plate_num')
    loss = serializers.SerializerMethodField()
    is_different = serializers.SerializerMethodField()
    reason = serializers.SerializerMethodField()
    loss_rate = serializers.SerializerMethodField()

    class Meta:
        model = m.Job
        fields = (
            'vehicle',
            'started_on',
            'total_mission_weight',
            'total_delivered_weight',
            'loss',
            'is_different',
            'reason',
            'loss_rate'
        )

    def get_loss(self, instance):
        return instance.total_delivered_weight - instance.total_mission_weight

    def get_is_different(self, instance):
        return '是' if instance.total_mission_weight != instance.total_delivered_weight else '不'

    def get_reason(self, instance):
        pass

    def get_loss_rate(self, instance):
        loss = instance.total_delivered_weight - instance.total_mission_weight
        return (loss / instance.total_mission_weight) * 1000
