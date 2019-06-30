from collections import defaultdict
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import serializers

from . import models as m
from ..core import constants as c
from ..core.utils import format_datetime

# models
from ..info.models import Station

# serializers
from ..core.serializers import TMSChoiceField
from ..account.serializers import ShortUserSerializer
from ..info.serializers import (
    ShortStationSerializer, ShortProductSerializer,
    ShortProductDisplaySerializer
)
from ..finance.serializers import (
    BillDocumentSerializer, ShortBillDocumentSerializer
)
from ..road.serializers import ShortRouteSerializer
from ..vehicle.serializers import ShortVehicleSerializer


class ShortOrderProductSerializer(serializers.ModelSerializer):

    product = ShortProductSerializer()

    class Meta:
        model = m.OrderProduct
        fields = (
            'product',
        )


class ShortOrderProductDeliverSerializer(serializers.ModelSerializer):

    unloading_station = ShortStationSerializer(
        read_only=True
    )

    order_product = ShortOrderProductSerializer(
        read_only=True
    )

    class Meta:
        model = m.OrderProductDeliver
        fields = (
            'id', 'unloading_station', 'order_product'
        )


class MissionWeightSerializer(serializers.ModelSerializer):

    vehicle = ShortVehicleSerializer(source='job.vehicle')
    driver = ShortUserSerializer(source='job.driver')
    escort = ShortUserSerializer(source='job.escort')
    route = ShortUserSerializer(source='job.route')

    class Meta:
        model = m.Mission
        fields = (
            'id', 'mission_weight', 'vehicle', 'driver', 'escort', 'route'
        )


class OrderProductDeliverSerializer(serializers.ModelSerializer):
    """
    Serializer for unloading stations selected for product delivery
    """
    unloading_station = ShortStationSerializer(
        read_only=True
    )
    jobs = serializers.SerializerMethodField()

    class Meta:
        model = m.OrderProductDeliver
        fields = (
            'id', 'unloading_station', 'due_time', 'weight',
            'jobs'
        )

    def get_jobs(self, instance):
        return MissionWeightSerializer(
            instance.missions.all(),
            many=True
        ).data


class OrderProductSerializer(serializers.ModelSerializer):
    """
    Serializer for ordred products
    """
    unloading_stations = OrderProductDeliverSerializer(
        source='orderproductdeliver_set', many=True, read_only=True
    )

    product = ShortProductSerializer(read_only=True)
    total_weight_measure_unit = TMSChoiceField(
        choices=c.PRODUCT_WEIGHT_MEASURE_UNIT
    )
    price_weight_measure_unit = TMSChoiceField(
        choices=c.PRODUCT_WEIGHT_MEASURE_UNIT
    )
    loss_unit = TMSChoiceField(
        choices=c.PRODUCT_WEIGHT_MEASURE_UNIT
    )
    payment_method = TMSChoiceField(
        choices=c.PAYMENT_METHOD
    )

    class Meta:
        model = m.OrderProduct
        exclude = (
            'order_loading_station',
        )


class OrderLoadingStationSerializer(serializers.ModelSerializer):
    """
    Serializer for ordred loading statins
    """
    loading_station = ShortStationSerializer(read_only=True)
    quality_station = ShortStationSerializer(read_only=True)
    products = OrderProductSerializer(
        source='orderproduct_set', many=True, read_only=True
    )

    class Meta:
        model = m.OrderLoadingStation
        exclude = (
            'order',
        )


class ShortOrderLoadingStationSerializer(serializers.ModelSerializer):

    loading_station = ShortStationSerializer(read_only=True)
    quality_station = ShortStationSerializer(read_only=True)

    class Meta:
        model = m.OrderLoadingStation
        fields = (
            'loading_station', 'quality_station'
        )


class OrderSerializer(serializers.ModelSerializer):
    """
    Order Create and Update Serializer
    """
    assignee = ShortUserSerializer(read_only=True)
    customer = ShortUserSerializer(read_only=True)
    order_source = TMSChoiceField(choices=c.ORDER_SOURCE, required=False)
    status = TMSChoiceField(choices=c.ORDER_STATUS, required=False)
    loading_stations = OrderLoadingStationSerializer(
        source='orderloadingstation_set', many=True, read_only=True
    )

    class Meta:
        model = m.Order
        fields = '__all__'

    def create(self, validated_data):
        """
        Request format
        {
            alias: alias,
            assignee: assignee_id,
            customer: customer_id,
            due_time: due_time,
            loading_stations: [
                {
                    loading_station: station_id,
                    quality_station: station_id,
                    products: [
                        product: product_id,
                        total_weight: total_weight
                        unloading_stations: [
                            {
                                unloading_station: station_id
                                weight: weight
                            }
                        ]
                    ]
                }
            ]
        }
        1. Validate the data
        2. save models

        Cannot use validate_<field> or validate because we need to
           write writable nested serializer

        todo: remove twice db get; one for validation, other for saving models
        """
        # 1. Validate the data
        # get loading stations data
        assignee_data = self.context.pop('assignee', None)
        if assignee_data is None:
            raise serializers.ValidationError({
                'assignee': 'Assignee data are missing'
            })

        try:
            assignee = m.User.objects.get(id=assignee_data.get('id', None))
        except m.User.DoesNotExist:
            raise serializers.ValidationError({
                'assignee': 'Such user does not exist'
            })

        customer_data = self.context.pop('customer', None)
        if customer_data is None:
            raise serializers.ValidationError({
                'customer': 'Customer data are missing'
            })

        try:
            customer = m.User.objects.get(id=customer_data.get('id', None))
        except m.User.DoesNotExist:
            raise serializers.ValidationError({
                'customer': 'Such customer does not exist'
            })

        loading_stations_data = self.context.pop('loading_stations', None)
        weight_errors = []
        if loading_stations_data is None:
            raise serializers.ValidationError({
                'order': 'Order data are missing'
            })

        for loading_station_data in loading_stations_data:
            products_data = loading_station_data.get(
                'products', None
            )
            if products_data is None:
                raise serializers.ValidationError({
                    'products': 'Order Product data are missing'
                })

            # validate product weights
            product_index = 0
            for product_data in products_data:
                unloading_stations_data = product_data.get(
                    'unloading_stations', None
                )
                if unloading_stations_data is None:
                    raise serializers.ValidationError({
                        'unloading_station':
                        'Unloading stations are not provided'
                    })
                total_weight = float(product_data.get('total_weight', 0))
                total_weight = float(total_weight)
                # TODO: check total weight validation

                for unloading_station_data in unloading_stations_data:
                    # TODO: check unloading station weight validation
                    weight = float(unloading_station_data.get('weight', 0))
                    total_weight = total_weight - weight

                if total_weight != 0:
                    weight_errors.append(product_index)
                product_index = product_index + 1

        if weight_errors:
            raise serializers.ValidationError({
                'weight': weight_errors
            })
        # 2. save models
        order = m.Order.objects.create(
            assignee=assignee,
            customer=customer,
            **validated_data
        )

        for loading_station_data in loading_stations_data:
            station_data = loading_station_data.pop('loading_station')
            if station_data is None:
                raise serializers.ValidationError({
                    'loading_station': 'Loading Station data are missing'
                })

            try:
                loading_station = Station.loadingstations.get(
                    id=station_data.get('id', None)
                )
            except Station.DoesNotExist:
                raise serializers.ValidationError({
                    'loading_station': 'Loading Station does not exists'
                })

            station_data = loading_station_data.pop('quality_station')
            if station_data is None:
                raise serializers.ValidationError({
                    'quality_station': 'Quality Station data are missing'
                })
            try:
                quality_station = Station.qualitystations.get(
                    pk=station_data.get('id')
                )
            except Station.DoesNotExist:
                raise serializers.ValidationError({
                    'quality_station': 'Quality Station does not exists'
                })

            products_data = loading_station_data.pop('products')

            order_loading_station = m.OrderLoadingStation.objects.create(
                order=order,
                loading_station=loading_station,
                quality_station=quality_station,
                **loading_station_data
            )

            for product_data in products_data:
                product = product_data.pop('product', None)
                if product is None:
                    raise serializers.ValidationError({
                        'product': 'Product data are missing'
                    })

                try:
                    product = m.Product.objects.get(
                        id=product.get('id')
                    )
                except m.Product.DoesNotExist:
                    raise serializers.ValidationError({
                        'product': 'Product does not exist'
                    })

                unloading_stations_data = product_data.pop(
                    'unloading_stations'
                )

                product_data['total_weight_measure_unit'] =\
                    product_data['total_weight_measure_unit']['value']
                product_data['price_weight_measure_unit'] =\
                    product_data['price_weight_measure_unit']['value']
                product_data['loss_unit'] =\
                    product_data['loss_unit']['value']
                product_data['payment_method'] =\
                    product_data['payment_method']['value']
                order_product = m.OrderProduct.objects.create(
                    order_loading_station=order_loading_station,
                    product=product,
                    **product_data
                )

                for unloading_station_data in unloading_stations_data:
                    station_data = unloading_station_data.pop('unloading_station')
                    if station_data is None:
                        raise serializers.ValidationError({
                            'unloading_station': 'Unloading Station data are missing'
                        })

                    unloading_station = Station.unloadingstations.get(
                        pk=station_data.get('id')
                    )
                    m.OrderProductDeliver.objects.create(
                        order_product=order_product,
                        unloading_station=unloading_station,
                        **unloading_station_data
                    )

        return order

    def update(self, instance, validated_data):
        """
        Request format
        {
            alias: alias,
            assignee: assignee_id,
            customer: customer_id,
            due_time: due_time,
            loading_stations:[
                {
                    loading_station: station_id,
                    quality_station: station_id,
                    products: [
                        product: product_id,
                        total_weight: total_weight
                        unloading_stations: [
                            {
                                unloading_station: station_id
                                weight: weight
                            }
                        ]
                    ]
                }
            ]
        }
        1. Validate the data
        2. save models

        Cannot use validate_<field> or validate because we need to
           write writable nested serializer

        todo: remove twice db get; one for validation, other for saving models
        """
        # 1. Validate the data
        # get loading stations data
        assignee_data = self.context.pop('assignee', None)
        if assignee_data is None:
            raise serializers.ValidationError({
                'assignee': 'Assignee data are missing'
            })

        try:
            assignee = m.User.objects.get(id=assignee_data.get('id', None))
        except m.User.DoesNotExist:
            raise serializers.ValidationError({
                'assignee': 'Such user does not exist'
            })

        customer_data = self.context.pop('customer', None)
        if customer_data is None:
            raise serializers.ValidationError({
                'customer': 'Customer data are missing'
            })

        try:
            customer = m.User.objects.get(id=customer_data.get('id', None))
        except m.User.DoesNotExist:
            raise serializers.ValidationError({
                'customer': 'Such customer does not exist'
            })

        loading_stations_data = self.context.pop('loading_stations', None)
        weight_errors = []
        if loading_stations_data is None:
            raise serializers.ValidationError({
                'order': 'Order data are missing'
            })

        for loading_station_data in loading_stations_data:
            products_data = loading_station_data.get(
                'products', None
            )
            if products_data is None:
                raise serializers.ValidationError({
                    'products': 'Order Product data are missing'
                })

            # validate product weights
            product_index = 0
            for product_data in products_data:
                unloading_stations_data = product_data.get(
                    'unloading_stations', None
                )
                if unloading_stations_data is None:
                    raise serializers.ValidationError({
                        'unloading_station':
                        'Unloading stations are not provided'
                    })
                total_weight = float(product_data.get('total_weight', 0))
                total_weight = float(total_weight)
                # TODO: check total weight validation

                for unloading_station_data in unloading_stations_data:
                    # TODO: check unloading station weight validation
                    weight = float(unloading_station_data.get('weight', 0))
                    total_weight = total_weight - weight

                if total_weight != 0:
                    weight_errors.append(product_index)
                product_index = product_index + 1

        if weight_errors:
            raise serializers.ValidationError({
                'weight': weight_errors
            })

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.assignee = assignee
        instance.customer = customer
        instance.save()
        instance.loading_stations.clear()
        # 2. save models
        for loading_station_data in loading_stations_data:
            station_data = loading_station_data.pop('loading_station')
            if station_data is None:
                raise serializers.ValidationError({
                    'loading_station': 'Loading Station data are missing'
                })

            try:
                loading_station = Station.loadingstations.get(
                    id=station_data.get('id', None)
                )
            except Station.DoesNotExist:
                raise serializers.ValidationError({
                    'loading_station': 'Loading Station does not exists'
                })

            station_data = loading_station_data.pop('quality_station')
            if station_data is None:
                raise serializers.ValidationError({
                    'quality_station': 'Quality Station data are missing'
                })
            try:
                quality_station = Station.qualitystations.get(
                    pk=station_data.get('id')
                )
            except Station.DoesNotExist:
                raise serializers.ValidationError({
                    'quality_station': 'Quality Station does not exists'
                })

            products_data = loading_station_data.pop('products')

            order_loading_station = m.OrderLoadingStation.objects.create(
                order=instance,
                loading_station=loading_station,
                quality_station=quality_station,
                **loading_station_data
            )

            for product_data in products_data:
                product = product_data.pop('product', None)
                if product is None:
                    raise serializers.ValidationError({
                        'product': 'Product data are missing'
                    })

                try:
                    product = m.Product.objects.get(
                        id=product.get('id')
                    )
                except m.Product.DoesNotExist:
                    raise serializers.ValidationError({
                        'product': 'Product does not exist'
                    })

                unloading_stations_data = product_data.pop(
                    'unloading_stations'
                )

                product_data['total_weight_measure_unit'] =\
                    product_data['total_weight_measure_unit']['value']
                product_data['price_weight_measure_unit'] =\
                    product_data['price_weight_measure_unit']['value']
                product_data['loss_unit'] =\
                    product_data['loss_unit']['value']
                product_data['payment_method'] =\
                    product_data['payment_method']['value']
                order_product = m.OrderProduct.objects.create(
                    order_loading_station=order_loading_station,
                    product=product,
                    **product_data
                )

                for unloading_station_data in unloading_stations_data:
                    station_data = unloading_station_data.pop('unloading_station')
                    unloading_station_data.pop('jobs')
                    if station_data is None:
                        raise serializers.ValidationError({
                            'unloading_station': 'Unloading Station data are missing'
                        })

                    unloading_station = Station.unloadingstations.get(
                        pk=station_data.get('id')
                    )
                    m.OrderProductDeliver.objects.create(
                        order_product=order_product,
                        unloading_station=unloading_station,
                        **unloading_station_data
                    )
        return instance


class ShortOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Order
        fields = (
            'id', 'alias'
        )


class OrderDataViewSerializer(serializers.ModelSerializer):
    """
    Order serializer
    """
    loading_stations = OrderLoadingStationSerializer(
        source='orderloadingstation_set', many=True, read_only=True
    )

    assignee = ShortUserSerializer(read_only=True)
    customer = ShortUserSerializer(read_only=True)
    order_source = TMSChoiceField(choices=c.ORDER_SOURCE)
    products = ShortProductSerializer(many=True)
    loading_stations_data = ShortStationSerializer(many=True)
    quality_stations_data = ShortStationSerializer(many=True)
    unloading_stations_data = ShortStationSerializer(many=True)
    status = TMSChoiceField(choices=c.ORDER_STATUS)

    class Meta:
        model = m.Order
        fields = '__all__'


class ShortMissionSerializer(serializers.ModelSerializer):

    mission = ShortOrderProductDeliverSerializer()

    class Meta:
        model = m.Mission
        fields = (
            'mission', 'mission_weight'
        )


class MissionSerializer(serializers.ModelSerializer):

    mission = ShortOrderProductDeliverSerializer()

    class Meta:
        model = m.Mission
        fields = (
            'mission_weight', 'loading_weight', 'unloading_weight',
            'arrived_station_on', 'started_unloading_on',
            'finished_unloading_on', 'departure_station_on',
            'is_completed', 'mission'
        )


class ShortJobSerializer(serializers.ModelSerializer):

    driver = ShortUserSerializer()
    escort = ShortUserSerializer()
    vehicle = ShortVehicleSerializer()
    route = ShortRouteSerializer()
    missions = ShortMissionSerializer(
        source='mission_set', many=True, read_only=True
    )

    class Meta:
        model = m.Job
        fields = (
            'driver', 'escort', 'vehicle', 'missions', 'route'
        )


class JobSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Job
        fields = '__all__'

    def create(self, validated_data):
        mission_ids = self.context.get('mission_ids')
        mission_weights = self.context.get('mission_weights')
        job = m.Job.objects.create(**validated_data)
        stations = job.route.stations[2:]

        for i, mission_id in enumerate(mission_ids):
            mission = get_object_or_404(m.OrderProductDeliver, pk=mission_id)
            m.Mission.objects.create(
                mission=mission,
                job=job,
                step=stations.index(mission.unloading_station),
                mission_weight=mission_weights[i]
            )
        return job


class JobProgressBarField(serializers.Field):

    def to_representation(self, instance):
        ret = []
        if instance.route is not None:
            ret.append({'title': '出发'})
            ret.append({'title': '赶往装货地'})
            ret.append({'title': '到达等待装货'})
            ret.append({'title': '开始装货'})
            ret.append({'title': '录入装货数量'})
            ret.append({'title': '赶往质检地'})
            ret.append({'title': '到达等待质检'})
            ret.append({'title': '开始质检'})
            ret.append({'title': '录入质检量'})

            unloading_stations = instance.route.stations[2:]
            for station in unloading_stations:
                ret.append({'title': '赶往卸货地:' + station.name})
                ret.append({'title': '到达等待卸货:' + station.name})
                ret.append({'title': '开始卸货:' + station.name})
                ret.append({'title': '录入卸货数量:' + station.name})

            progress = 1
            for item in ret:
                item['progress'] = progress
                item['active'] = progress == instance.progress
                progress = progress + 1

            ret.append({
                'title': '完成', 'progress': c.JOB_PROGRESS_COMPLETE,
                'active': instance.progress == c.JOB_PROGRESS_COMPLETE
            })
        return ret


class StationField(serializers.ListField):

    def to_representation(self, instance):
        if instance.route is not None:
            serializer = ShortStationSerializer(
                instance.route.stations, many=True
            )
            return serializer.data
        else:
            return []


class JobDataViewSerializer(serializers.ModelSerializer):

    vehicle = ShortVehicleSerializer()
    driver = ShortUserSerializer()
    escort = ShortUserSerializer()
    stations = StationField(source='*')
    products = ShortProductDisplaySerializer(
        source='order.products', many=True
    )
    progress_bar = JobProgressBarField(source='*')

    class Meta:
        model = m.Job
        fields = (
            'id', 'vehicle', 'driver', 'escort', 'stations', 'products',
            'progress', 'progress_bar', 'total_weight',
            'start_due_time', 'finish_due_time', 'route'
        )


class JobMileageField(serializers.Field):

    def to_representation(self, instance):
        return {
            'total_mileage': instance.total_mileage,
            'highway_mileage': instance.highway_mileage,
            'normalway_mileage': instance.normalway_mileage,
            'empty_mileage': instance.empty_mileage,
            'heavy_mileage':  instance.heavy_mileage
        }


class JobDeliverField(serializers.Field):

    def to_representation(self, instance):
        ret = []
        for mission in instance.mission_set.all():
            ret.append({
                'mission_weight': mission.mission_weight,
                'loading_weight': mission.loading_weight,
                'unloading_weight': mission.unloading_weight
            })
        return ret


class JobDoneSerializer(serializers.ModelSerializer):
    """
    Job overview serializer for driver app
    """
    products = ShortProductDisplaySerializer(
        source='order.products',
        many=True
    )
    escort = ShortUserSerializer()
    stations = StationField(source='*')
    mileage = JobMileageField(source='*')
    delivers = JobDeliverField(source='*')
    bills = serializers.SerializerMethodField()

    class Meta:
        model = m.Job
        fields = (
            'id', 'started_on', 'finished_on', 'products', 'total_weight',
            'escort', 'stations', 'mileage', 'delivers', 'bills'
        )

    def get_bills(self, job):
        bill_type = self.context.get('bill_type', 'all')

        bills = job.bills.all()
        if bill_type == 'station':
            bills = bills.filter(
                category__in=[
                    c.BILL_FROM_LOADING_STATION, c.BILL_FROM_QUALITY_STATION,
                    c.BILL_FROM_UNLOADING_STATION
                ]
            )
        elif bill_type == 'other':
            bills = bills.filter(
                category__in=[
                    c.BILL_FROM_OIL_STATION, c.BILL_FROM_TRAFFIC,
                    c.BILL_FROM_OTHER
                ]
            )

        bills_by_categories = defaultdict(lambda: defaultdict(list))

        for bill in bills:
            bills_by_categories[bill.category][bill.sub_category].append(bill)

        new_bills = []
        category_choices = dict((x, y) for x, y in c.BILL_CATEGORY)

        for category, group_by_category in bills_by_categories.items():
            bills_by_subcategories = []
            if category == c.BILL_FROM_LOADING_STATION:
                sub_categories = c.LOADING_STATION_BILL_SUB_CATEGORY
            elif category == c.BILL_FROM_QUALITY_STATION:
                sub_categories = c.QUALITY_STATION_BILL_SUB_CATEGORY
            elif category == c.BILL_FROM_UNLOADING_STATION:
                sub_categories = c.UNLOADING_STATION_BILL_SUB_CATEGORY
            elif category == c.BILL_FROM_OIL_STATION:
                sub_categories = c.OIL_BILL_SUB_CATEGORY
            elif category == c.BILL_FROM_TRAFFIC:
                sub_categories = c.TRAFFIC_BILL_SUB_CATEGORY
            elif category == c.BILL_FROM_OTHER:
                sub_categories = c.OTHER_BILL_SUB_CATEGORY
            sub_category_choices = dict((x, y) for x, y in sub_categories)

            for sub_category, group_by_sub_category in group_by_category.items():
                bills_by_subcategories.append({
                    'sub_category': {
                        'value': sub_category,
                        'text': sub_category_choices[sub_category]
                    },
                    'data': ShortBillDocumentSerializer(
                        group_by_sub_category,
                        many=True
                    ).data
                })
            new_bills.append({
                'category': {
                    'value': category,
                    'text': category_choices[category]
                },
                'data': bills_by_subcategories
            })
        return new_bills


class JobBillViewSerializer(serializers.ModelSerializer):
    """
    job bill view serializer for driver app
    """
    bills = serializers.SerializerMethodField()
    stations = StationField(source='*')

    class Meta:
        model = m.Job
        fields = (
            'id', 'bills', 'stations', 'finished_on'
        )

    def get_bills(self, job):
        bill_type = self.context.get('bill_type', 'all')
        bill_type = bill_type.lower()
        bill_types = bill_type.split(',')
        category_filter = Q()

        if 'oil' in bill_types:
            category_filter |= Q(category=c.BILL_FROM_OIL_STATION)

        if 'traffic' in bill_type:
            category_filter |= Q(category=c.BILL_FROM_TRAFFIC)

        if 'other' in bill_type:
            category_filter |= Q(category=c.BILL_FROM_OIL_STATION) |\
                               Q(category=c.BILL_FROM_TRAFFIC) |\
                               Q(category=c.BILL_FROM_OTHER)

        if 'station' in bill_types:
            pass

        bills = job.bills.all()
        if category_filter:
            bills = bills.filter(category_filter)

        bills_by_categories = defaultdict(lambda: defaultdict(list))

        for bill in bills:
            bills_by_categories[bill.category][bill.sub_category].append(bill)

        new_bills = []
        category_choices = dict((x, y) for x, y in c.BILL_CATEGORY)

        for category, group_by_category in bills_by_categories.items():
            bills_by_subcategories = []
            if category == c.BILL_FROM_LOADING_STATION:
                sub_categories = c.LOADING_STATION_BILL_SUB_CATEGORY
            elif category == c.BILL_FROM_QUALITY_STATION:
                sub_categories = c.QUALITY_STATION_BILL_SUB_CATEGORY
            elif category == c.BILL_FROM_UNLOADING_STATION:
                sub_categories = c.UNLOADING_STATION_BILL_SUB_CATEGORY
            elif category == c.BILL_FROM_OIL_STATION:
                sub_categories = c.OIL_BILL_SUB_CATEGORY
            elif category == c.BILL_FROM_TRAFFIC:
                sub_categories = c.TRAFFIC_BILL_SUB_CATEGORY
            elif category == c.BILL_FROM_OTHER:
                sub_categories = c.OTHER_BILL_SUB_CATEGORY
            sub_category_choices = dict((x, y) for x, y in sub_categories)

            for sub_category, group_by_sub_category in group_by_category.items():
                bills_by_subcategories.append({
                    'sub_category': {
                        'value': sub_category,
                        'text': sub_category_choices[sub_category]
                    },
                    'data': BillDocumentSerializer(
                        group_by_sub_category,
                        context={'request': self.context.get('request')},
                        many=True
                    ).data
                })
            new_bills.append({
                'category': {
                    'value': category,
                    'text': category_choices[category]
                },
                'data': bills_by_subcategories
            })
        return new_bills


class JobProgressSerializer(serializers.ModelSerializer):

    progress_bar = JobProgressBarField(source='*')

    class Meta:
        model = m.Job
        fields = (
            'id', 'progress_bar'
        )


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


class LoadingStationTimeField(serializers.Field):

    def to_representation(self, value):
        ret = {
            "arrived_on": format_datetime(value.arrived_loading_station_on),
            "started_working_on": format_datetime(value.started_loading_on),
            "finished_working_on": format_datetime(value.finished_loading_on),
            "departure_on": format_datetime(value.departure_loading_station_on)
        }
        return ret

    def to_internal_value(self, data):
        ret = {
            "arrived_loading_station_on": data['arrived_on']
        }
        return ret


class QualityStationTimeField(serializers.Field):

    def to_representation(self, value):
        ret = {
            "arrived_on": format_datetime(value.arrived_quality_station_on),
            "started_working_on": format_datetime(value.started_checking_on),
            "finished_working_on": format_datetime(value.finished_checking_on),
            "departure_on": format_datetime(value.departure_quality_station_on)
        }
        return ret

    def to_internal_value(self, data):
        ret = {
            "arrived_loading_station_on": data['arrived_on']
        }
        return ret


class UnLoadingStationTimeField(serializers.Field):
    def to_representation(self, value):
        ret = []
        for station in value.all():
            ret.append({
                "arrived_on":
                    format_datetime(station.arrived_station_on),
                "started_working_on":
                    format_datetime(station.started_unloading_on),
                "finished_working_on":
                    format_datetime(station.finished_unloading_on),
                "departure_on":
                    format_datetime(station.departure_station_on)
            })

        return ret

    def to_internal_value(self, data):
        pass


class JobTimeSerializer(serializers.ModelSerializer):

    order = ShortOrderSerializer()
    vehicle = ShortVehicleSerializer()
    driver = ShortUserSerializer()
    escort = ShortUserSerializer()
    loading_station_time = LoadingStationTimeField(source='*')
    quality_station_time = QualityStationTimeField(source='*')
    unloading_station_time = UnLoadingStationTimeField(source='mission_set')

    class Meta:
        model = m.Job
        fields = (
            'id', 'order', 'vehicle', 'driver', 'escort', 'started_on',
            'finished_on', 'loading_station_time', 'quality_station_time',
            'unloading_station_time'
        )


class JobCostSerializer(serializers.ModelSerializer):

    order = ShortOrderSerializer()
    vehicle = ShortVehicleSerializer()
    bills = BillDocumentSerializer(many=True)

    class Meta:
        model = m.Job
        fields = (
            'id', 'order', 'vehicle', 'bills'
        )


class DriverJobReportSerializer(serializers.ModelSerializer):

    year = serializers.CharField(source='month.year')
    month = serializers.CharField(source='month.month')

    class Meta:
        model = m.JobReport
        fields = (
            'year', 'month', 'total_mileage', 'empty_mileage',
            'heavy_mileage', 'highway_mileage', 'normalway_mileage'
        )


class JobReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.JobReport
        fields = '__all__'
