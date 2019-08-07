# from collections import defaultdict
# from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone as datetime
from rest_framework import serializers

from . import models as m
from ..core import constants as c
# from ..core.utils import format_datetime

# models
from ..hr.models import CustomerProfile
from ..info.models import Station, Product

# serializers
from ..core.serializers import TMSChoiceField, Base64ImageField
from ..account.serializers import ShortUserSerializer
from ..hr.serializers import ShortCustomerProfileSerializer
from ..info.serializers import (
    ShortStationSerializer, ShortProductSerializer
)
from ..info.serializers import ShortRouteSerializer
from ..vehicle.serializers import ShortVehicleSerializer


class OrderCartUnloadingStationSerializer(serializers.ModelSerializer):

    unloading_station = ShortStationSerializer(read_only=True)

    class Meta:
        model = m.OrderCartUnloadingStation
        exclude = ('item', )


class OrderCartSerializer(serializers.ModelSerializer):

    product = ShortProductSerializer(read_only=True)
    loading_station = ShortStationSerializer(read_only=True)
    quality_station = ShortStationSerializer(read_only=True)
    unloading_stations = OrderCartUnloadingStationSerializer(
        source='ordercartunloadingstation_set', many=True, read_only=True
    )

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

        # loading station validation
        loading_station_data = self.context.get('loading_station', None)
        if loading_station_data is None:
            raise serializers.ValidationError({
                'loading_station': 'Loading Station data is missing'
            })

        try:
            loading_station = Station.loadingstations.get(
                id=loading_station_data.get('id', None)
            )
        except Station.DoesNotExist:
            raise serializers.ValidationError({
                'loading_station': 'Such Loading Station does not exist'
            })

        # quality station validation
        quality_station_data = self.context.get('quality_station', None)
        if quality_station_data is None:
            raise serializers.ValidationError({
                'quality_station': 'Quality Station data is missing'
            })

        try:
            quality_station = Station.qualitystations.get(
                id=quality_station_data.get('id', None)
            )
        except Station.DoesNotExist:
            raise serializers.ValidationError({
                'loading_station': 'Such Quality Station does not exist'
            })

        unloading_stations_data = self.context.get('unloading_stations', None)
        unloading_weights = 0
        for unloading_station_data in unloading_stations_data:
            unloading_weights += unloading_station_data.get('weight', 0)

        if unloading_weights > validated_data.get('weight', 0):
            raise serializers.ValidationError({
                'weight':
                'Sum of unloading stations weight exceed the product weight'
            })

        # create cart item
        cart_item = m.OrderCart.objects.create(
            product=product,
            loading_station=loading_station,
            quality_station=quality_station,
            **validated_data
        )

        unloading_stations_data = self.context.get('unloading_stations', None)
        for unloading_station_data in unloading_stations_data:
            station_data = unloading_station_data.pop('unloading_station')
            unloading_station = get_object_or_404(
                Station, id=station_data.get('id', None)
            )
            m.OrderCartUnloadingStation.objects.create(
                item=cart_item,
                unloading_station=unloading_station,
                **unloading_station_data
            )

        return cart_item

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

        # loading station validation
        loading_station_data = self.context.get('loading_station', None)
        if loading_station_data is None:
            raise serializers.ValidationError({
                'loading_station': 'Loading Station data is missing'
            })

        try:
            loading_station = Station.loadingstations.get(
                id=loading_station_data.get('id', None)
            )
        except Station.DoesNotExist:
            raise serializers.ValidationError({
                'loading_station': 'Such Loading Station does not exist'
            })

        # quality station validation
        quality_station_data = self.context.get('quality_station', None)
        if quality_station_data is None:
            raise serializers.ValidationError({
                'quality_station': 'Quality Station data is missing'
            })

        try:
            quality_station = Station.qualitystations.get(
                id=quality_station_data.get('id', None)
            )
        except Station.DoesNotExist:
            raise serializers.ValidationError({
                'loading_station': 'Such Quality Station does not exist'
            })

        unloading_stations_data = self.context.get('unloading_stations', None)
        unloading_weights = 0
        for unloading_station_data in unloading_stations_data:
            unloading_weights += unloading_station_data.get('weight', 0)

        if unloading_weights > validated_data.get('weight', 0):
            raise serializers.ValidationError({
                'weight':
                'Sum of unloading stations weight exceed the product weight'
            })

        instance.product = product
        instance.loading_station = loading_station
        instance.quality_station = quality_station

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        instance.unloading_stations.clear()

        unloading_stations_data = self.context.get('unloading_stations', None)
        for unloading_station_data in unloading_stations_data:
            station_data = unloading_station_data.pop('unloading_station')
            unloading_station = get_object_or_404(
                Station, id=station_data.get('id', None)
            )
            m.OrderCartUnloadingStation.objects.create(
                item=instance,
                unloading_station=unloading_station,
                **unloading_station_data
            )
        return instance


# class ShortOrderProductSerializer(serializers.ModelSerializer):

#     product = ShortProductSerializer()

#     class Meta:
#         model = m.OrderProduct
#         fields = (
#             'product',
#         )


# class ShortOrderProductDeliverSerializer(serializers.ModelSerializer):

#     unloading_station = ShortStationSerializer(
#         read_only=True
#     )

#     order_product = ShortOrderProductSerializer(
#         read_only=True
#     )

#     class Meta:
#         model = m.OrderProductDeliver
#         fields = (
#             'id', 'unloading_station', 'order_product'
#         )


# class OrderProductDeliverMissionSerializer(serializers.ModelSerializer):

#     job_id = serializers.CharField(source='job.id')
#     vehicle = ShortVehicleSerializer(source='job.vehicle')
#     driver = ShortUserSerializer(source='job.driver')
#     escort = ShortUserSerializer(source='job.escort')
#     route = ShortUserSerializer(source='job.route')

#     class Meta:
#         model = m.Mission
#         fields = (
#             'id', 'job_id', 'mission_weight', 'vehicle', 'driver', 'escort',
#             'route'
#         )


class ShortJobSerializer(serializers.ModelSerializer):

    driver = ShortUserSerializer()
    escort = ShortUserSerializer()
    vehicle = ShortVehicleSerializer()
    route = ShortRouteSerializer()

    class Meta:
        model = m.Job
        fields = (
            'id', 'vehicle', 'driver', 'escort', 'route'
        )


class OrderProductDeliverSerializer(serializers.ModelSerializer):
    """
    Order Product Deliver Serializer
    """
    unloading_station = ShortStationSerializer(read_only=True)

    class Meta:
        model = m.OrderProductDeliver
        fields = (
            'id', 'unloading_station', 'arriving_due_time', 'weight',
        )


class OrderProductDeliverAdminAppSerializer(OrderProductDeliverSerializer):
    """
    Order Product Deliver Serializer for Web manager
    """
    job_delivers = serializers.SerializerMethodField()

    class Meta(OrderProductDeliverSerializer.Meta):
        fields = (
            'id', 'unloading_station', 'arriving_due_time', 'weight',
            'job_delivers'
        )

    def get_job_delivers(self, instance):
        ret = []
        for job_deliver in instance.job_delivers.all():
            job = job_deliver.job_station.job
            ret.append({
                'id': job_deliver.job_station.job.id,
                'vehicle': ShortVehicleSerializer(job.vehicle).data,
                'driver': ShortUserSerializer(job.driver).data,
                'escort': ShortUserSerializer(job.escort).data,
                'route': ShortRouteSerializer(job.route).data,
                'mission_weight': job_deliver.mission_weight,
            })
        return ret


class OrderProductDeliverCustomerAppSerializer(OrderProductDeliverSerializer):
    """
    Order Product Deliver Serializer for Customer manager
    """
    pass


class OrderProductSerializer(serializers.ModelSerializer):
    """
    Serializer for ordred products
    """
    product = ShortProductSerializer(read_only=True)
    weight_measure_unit = TMSChoiceField(
        choices=c.PRODUCT_WEIGHT_MEASURE_UNIT
    )

    class Meta:
        model = m.OrderProduct
        exclude = (
            'order',
        )


class OrderProductAdminAppSerializer(OrderProductSerializer):
    """
    Serializer for Order product for admin manager
    """
    unloading_stations = OrderProductDeliverAdminAppSerializer(
        source='orderproductdeliver_set', many=True, read_only=True
    )


class OrderProductCustomerAppSerializer(OrderProductSerializer):
    """
    Serializer for Order product for customer app
    """
    unloading_stations = OrderProductDeliverCustomerAppSerializer(
        source='orderproductdeliver_set', many=True, read_only=True
    )


class ShortOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Order
        fields = (
            'id', 'alias'
        )


class OrderSerializer(serializers.ModelSerializer):
    """
    order model serializer
    """
    assignee = ShortUserSerializer()
    customer = ShortCustomerProfileSerializer()
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

        # save models
        order = m.Order.objects.create(
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
        ret['assignee'] = get_object_or_404(m.User, id=data['assignee']['id'])
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


# class ShortJobSerializer(serializers.ModelSerializer):

#     driver = ShortUserSerializer()
#     escort = ShortUserSerializer()
#     vehicle = ShortVehicleSerializer()
#     route = ShortRouteSerializer()
#     missions = ShortMissionSerializer(
#         source='mission_set', many=True, read_only=True
#     )

#     mileage = JobMileageField(source='*')

#     class Meta:
#         model = m.Job
#         fields = (
#             'driver', 'escort', 'vehicle', 'missions', 'route', 'mileage'
#         )


class ShortJobStationProductSerializer(serializers.ModelSerializer):

    product = ShortProductSerializer(read_only=True)

    class Meta:
        model = m.JobStationProduct
        fields = (
            'id', 'product', 'mission_weight', 'weight'
        )


class JobStationProductSerializer(serializers.ModelSerializer):

    product = ShortProductSerializer(read_only=True)

    class Meta:
        model = m.JobStationProduct
        exclude = (
            'job_station',
        )


class JobStationProductDocumentSerializer(serializers.ModelSerializer):

    document = Base64ImageField()

    class Meta:
        model = m.JobStationProduct
        fields = (
            'document', 'weight'
        )


class ShortJobStationSerializer(serializers.ModelSerializer):

    station = ShortStationSerializer()
    products = ShortJobStationProductSerializer(
        source='jobstationproduct_set', many=True, read_only=True
    )

    class Meta:
        model = m.JobStation
        fields = (
            'id', 'station', 'products'
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


class JobAdminSerializer(serializers.ModelSerializer):

    vehicle = ShortVehicleSerializer()
    driver = ShortUserSerializer()
    escort = ShortUserSerializer()
    loading_station = serializers.SerializerMethodField()
    due_time = serializers.SerializerMethodField()
    quality_station = serializers.SerializerMethodField()
    route = ShortRouteSerializer()
    branches = serializers.SerializerMethodField()
    branch_options = serializers.SerializerMethodField()

    class Meta:
        model = m.Job
        fields = (
            'id', 'vehicle', 'driver', 'escort', 'loading_station',
            'quality_station', 'due_time', 'route', 'branches',
            'branch_options'
        )

    def get_loading_station(self, instance):
        return ShortStationSerializer(
            instance.stations.all()[0]
        ).data

    def get_due_time(self, instance):
        return instance.jobstation_set.all()[0].due_time

    def get_quality_station(self, instance):
        return ShortStationSerializer(
            instance.stations.all()[0]
        ).data

    def get_branch_options(self, instance):
        options = []
        for i in range(0, instance.vehicle.branch_count):
            options.append({
                'id': i
            })

        return options

    def get_branches(self, instance):
        branches = []
        for job_station in instance.jobstation_set.all():
            for job_station_product in job_station.jobstationproduct_set.all():
                for product_branch in job_station_product.branches:
                    for branch in branches:
                        if product_branch == branch['branch']['id']:
                            branch['mission_weight'] += job_station_product.mission_weight
                            branch['unloading_stations'].append({
                                'unloading_station': ShortStationSerializer(job_station.station).data,
                                'mission_weight': job_station_product.mission_weight
                            })
                            break
                    else:
                        branches.append({
                            'branch': {'id': product_branch},
                            'product': ShortProductSerializer(job_station_product.product).data,
                            'mission_weight': job_station_product.mission_weight,
                            'unloading_stations': [{
                                'unloading_station': ShortStationSerializer(job_station.station).data,
                                'due_time': job_station.due_time,
                                'mission_weight': job_station_product.mission_weight
                            }]
                        })

        return branches


class JobSerializer(serializers.ModelSerializer):

    vehicle = ShortVehicleSerializer()
    driver = ShortUserSerializer()
    escort = ShortUserSerializer()
    loading_station = serializers.SerializerMethodField()
    quality_station = serializers.SerializerMethodField()
    unloading_stations = serializers.SerializerMethodField()
    mileage = JobMileageField(source='*')

    class Meta:
        model = m.Job
        fields = (
            'id', 'vehicle', 'driver', 'escort', 'loading_station',
            'quality_station', 'unloading_stations', 'total_weight',
            'mileage'
        )

    def get_loading_station(self, instance):
        return ShortStationSerializer(
            instance.stations.all()[0]
        ).data

    def get_quality_station(self, instance):
        return ShortStationSerializer(
            instance.stations.all()[0]
        ).data

    def get_unloading_stations(self, instance):
        return ShortStationSerializer(
            instance.stations.all()[2:], many=True
        ).data


class JobCurrentSerializer(serializers.ModelSerializer):
    """
    Serializer for current job for driver app
    """
    order_id = serializers.CharField(source='order.id')
    plate_num = serializers.CharField(source='vehicle.plate_num')
    driver = serializers.CharField(source='driver.name')
    escort = serializers.CharField(source='escort.name')
    total_distance = serializers.IntegerField(source='route.distance')
    stations = ShortJobStationSerializer(
        source='jobstation_set', many=True, read_only=True
    )
    progress_bar = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = m.Job
        fields = (
            'id', 'order_id', 'plate_num', 'driver', 'escort',
            'total_distance', 'stations', 'progress', 'progress_bar', 'route'
        )

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


class JobDoneSerializer(serializers.ModelSerializer):
    """
    Serializer for completed jobs in driver app
    """
    order_id = serializers.CharField(source='order.id')
    plate_num = serializers.CharField(source='vehicle.plate_num')
    total_distance = serializers.IntegerField(source='route.distance')
    stations = ShortJobStationSerializer(
        source='jobstation_set', many=True, read_only=True
    )
    driver = serializers.CharField(source='driver.name')
    escort = serializers.CharField(source='escort.name')
    mileage = JobMileageField(source='*')

    class Meta:
        model = m.Job
        fields = (
            'id', 'order_id', 'plate_num', 'total_distance', 'stations',
            'started_on', 'finished_on',
            'total_weight', 'driver', 'escort',
            'mileage'
        )


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


class JobBillSerializer(serializers.ModelSerializer):

    document = Base64ImageField()
    category = TMSChoiceField(choices=c.BILL_CATEGORY)
    sub_category = BillSubCategoyChoiceField(source='*', required=False)
    detail_category = BillDetailCategoyChoiceField(source='*', required=False)

    class Meta:
        model = m.JobBill
        fields = '__all__'


# class NewJobBillViewSerializer(serializers.ModelSerializer):

#     bills = BillDocumentSerializer(many=True)

#     class Meta:
#         model = m.Job
#         fields = (
#             'id', 'bills'
#         )


class JobBillViewSerializer(serializers.Serializer):
    """
    job bill view serializer for driver app
    """
    document = serializers.ImageField(required=False)
    category = serializers.CharField(required=False)
    amount = serializers.FloatField(required=False)
    unit_price = serializers.FloatField(required=False)
    cost = serializers.FloatField(required=False)
    weight = serializers.FloatField(required=False)


class JobMileageSerializer(serializers.ModelSerializer):

    order = ShortOrderSerializer()
    vehicle = ShortVehicleSerializer()
    driver = ShortUserSerializer()
    escort = ShortUserSerializer()

    class Meta:
        model = m.Job
        fields = (
            'id', 'order', 'vehicle', 'driver', 'escort', 'total_mileage',
            'empty_mileage', 'heavy_mileage', 'highway_mileage',
            'normalway_mileage'
        )


class JobDocumentSerializer(serializers.ModelSerializer):

    order = ShortOrderSerializer()
    vehicle = ShortVehicleSerializer()
    bills_by_category = serializers.SerializerMethodField()

    class Meta:
        model = m.Job
        fields = (
            'id', 'order', 'vehicle', 'bills_by_category'
        )

    def get_bills_by_category(self, instance):
        ret = {}
        bills = instance.bills.all()
        for bill in bills:
            category = bill.category
            if category in ret:
                ret[category]['total_cost'] += bill.cost

                if category == c.BILL_FROM_OIL_STATION:
                    sub_categories = c.OIL_BILL_SUB_CATEGORY
                elif category == c.BILL_FROM_TRAFFIC:
                    sub_categories = c.TRAFFIC_BILL_SUB_CATEGORY
                elif category == c.BILL_FROM_OTHER:
                    sub_categories == c.OTHER_BILL_SUB_CATEGORY

                sub_category = bill.sub_category
                if sub_category in ret[category]['documents']:
                    ret[category]['documents'][sub_category].append({
                        'cost': bill.cost
                    })
                else:
                    ret[category]['documents'][sub_category] = [{
                        'cost': bill.cost
                    }]
            else:
                ret[category] = {
                    'total_cost': bill.cost,
                    'documents': {
                        bill.sub_category: [{
                            'cost': bill.cost
                        }]
                    }
                }
        return ret


class JobTimeDurationSerializer(serializers.ModelSerializer):
    """
    This serializer is used for displaying time duration
    """
    order = ShortOrderSerializer()
    vehicle = ShortVehicleSerializer()
    driver = ShortUserSerializer()
    escort = ShortUserSerializer()
    total_time = serializers.SerializerMethodField()
    durations = serializers.SerializerMethodField()

    class Meta:
        model = m.Job
        fields = (
            'id', 'order', 'vehicle', 'driver', 'escort',
            'total_time', 'durations'
        )

    def get_total_time(self, instance):
        if instance.started_on is None:
            return None

        finished_on = instance.finished_on
        if finished_on is None:
            finished_on = datetime.now()

        return round(
            (finished_on - instance.started_on).total_seconds() / 60
        )

    def get_durations(self, instance):
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

        station_duration = []
        for i in range(len(time_list) - 1):
            if i % 4 == 0:
                station_duration = []
            elif i % 4 == 3:
                durations.append(station_duration)

            station_duration.append(
                round(
                    (time_list[i + 1] - time_list[i]).total_seconds() / 60
                )
            )

        return durations


# class JobCostSerializer(serializers.ModelSerializer):

#     order = ShortOrderSerializer()
#     vehicle = ShortVehicleSerializer()
#     bills = BillDocumentSerializer(many=True)

#     class Meta:
#         model = m.Job
#         fields = (
#             'id', 'order', 'vehicle', 'bills'
#         )


class DriverJobReportSerializer(serializers.ModelSerializer):

    year = serializers.CharField(source='month.year')
    month = serializers.CharField(source='month.month')

    class Meta:
        model = m.JobReport
        fields = (
            'year', 'month', 'total_mileage', 'empty_mileage',
            'heavy_mileage', 'highway_mileage', 'normalway_mileage'
        )


# class JobReportSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = m.JobReport
#         fields = '__all__'


class VehicleStatusOrderSerializer(serializers.Serializer):

    id = serializers.CharField()
    plate_num = serializers.CharField()
    # progress = serializers.CharField()
    # client_name = serializers.CharField()
    distance = serializers.DecimalField(max_digits=8, decimal_places=2)
    duration = serializers.DecimalField(max_digits=5, decimal_places=1)
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
    products = ShortProductSerializer(source='order.products', many=True)
    driver = ShortUserSerializer(read_only=True)
    escort = ShortUserSerializer(read_only=True)

    class Meta:
        model = m.Job
        fields = (
            'id', 'alias', 'products', 'driver', 'escort', 'started_on',
            'finished_on'
        )


class JobBillDocumentForDriverSerializer(serializers.ModelSerializer):

    order_id = serializers.CharField(source='order.id')
    bills = serializers.SerializerMethodField()

    class Meta:
        model = m.Job
        fields = (
            'id', 'order_id', 'finished_on', 'bills'
        )

    def get_bills(self, instance):
        """
        todo; optimize the code
        """
        request = self.context.get('request')
        bill_type = self.context.get('bill_type', 'all')
        ret = {}
        bills = instance.bills.all()
        if bill_type != 'all':
            bills = bills.filter(category=bill_type)

        for bill in bills:
            category = bill.category
            if category in ret:
                ret[category]['total_cost'] += bill.cost

                if category == c.BILL_FROM_OIL_STATION:
                    sub_categories = c.OIL_BILL_SUB_CATEGORY
                elif category == c.BILL_FROM_TRAFFIC:
                    sub_categories = c.TRAFFIC_BILL_SUB_CATEGORY
                elif category == c.BILL_FROM_OTHER:
                    sub_categories == c.OTHER_BILL_SUB_CATEGORY

                sub_category = bill.sub_category
                if sub_category in ret[category]['documents']:
                    ret[category]['documents'][sub_category]['sub_total_cost'] += bill.cost
                    ret[category]['documents'][sub_category]['documents'].append(
                        JobBillSerializer(
                            bill, context={'request': request}
                        ).data
                    )
                else:
                    ret[category]['documents'][sub_category] = {
                        'sub_total_cost': bill.cost,
                        'documents': [
                            JobBillSerializer(
                                bill, context={'request': request}
                            ).data
                        ]
                    }
            else:
                ret[category] = {
                    'total_cost': bill.cost,
                    'documents': {
                        bill.sub_category: {
                            'sub_total_cost': bill.cost,
                            'documents':
                            [JobBillSerializer(
                                bill, context={'request': request}
                            ).data]
                        }
                    }
                }
        return ret


class VehicleUserBindSerializer(serializers.ModelSerializer):

    vehicle = ShortVehicleSerializer()
    driver = ShortUserSerializer()
    escort = ShortUserSerializer()

    class Meta:
        model = m.VehicleUserBind
        fields = '__all__'

    def validate(self, data):
        vehicle = data['vehicle']
        driver = data['driver']
        escort = data['escort']

        if self.instance is None and m.VehicleUserBind.objects.filter(
            vehicle=vehicle
        ).exists():
            raise serializers.ValidationError({
                'vehicle': 'This vehicle bind already exits'
            })

        if self.instance is not None and m.VehicleUserBind.objects.exclude(
            id=self.instance.id
        ).filter(vehicle=vehicle).exists():
            raise serializers.ValidationError({
                'vehicle': 'This vehicle bind already exits'
            })

        if self.instance is None and m.VehicleUserBind.objects.filter(
            driver=driver
        ).exists():
            raise serializers.ValidationError({
                'driver': 'This vehicle bind already exits'
            })

        if self.instance is not None and m.VehicleUserBind.objects.exclude(
            id=self.instance.id
        ).filter(driver=driver).exists():
            raise serializers.ValidationError({
                'driver': 'This driver bind already exits'
            })

        if self.instance is None and m.VehicleUserBind.objects.filter(
            escort=escort
        ).exists():
            raise serializers.ValidationError({
                'escort': 'This escort bind already exits'
            })

        if self.instance is not None and m.VehicleUserBind.objects.exclude(
            id=self.instance.id
        ).filter(escort=escort).exists():
            raise serializers.ValidationError({
                'escort': 'This escort bind already exits'
            })

        return data

    def to_internal_value(self, data):
        ret = {
            'vehicle': get_object_or_404(m.Vehicle, id=data['vehicle']['id']),
            'driver': get_object_or_404(m.User, id=data['driver']['id']),
            'escort': get_object_or_404(m.User, id=data['escort']['id'])
        }
        return ret
