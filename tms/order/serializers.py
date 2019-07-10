from collections import defaultdict
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import serializers

from . import models as m
from ..core import constants as c
from ..core.utils import format_datetime

# models
from ..hr.models import CustomerProfile
from ..info.models import Station

# serializers
from ..core.serializers import TMSChoiceField
from ..account.serializers import ShortUserSerializer
from ..hr.serializers import ShortCustomerProfileSerializer
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


class OrderProductDeliverMissionSerializer(serializers.ModelSerializer):

    job_id = serializers.CharField(source='job.id')
    vehicle = ShortVehicleSerializer(source='job.vehicle')
    driver = ShortUserSerializer(source='job.driver')
    escort = ShortUserSerializer(source='job.escort')
    route = ShortUserSerializer(source='job.route')

    class Meta:
        model = m.Mission
        fields = (
            'id', 'job_id', 'mission_weight', 'vehicle', 'driver', 'escort',
            'route'
        )


class OrderProductDeliverSerializer(serializers.ModelSerializer):
    """
    Serializer for unloading stations selected for product delivery
    """
    unloading_station = ShortStationSerializer(
        read_only=True
    )
    missions = serializers.SerializerMethodField()

    class Meta:
        model = m.OrderProductDeliver
        fields = (
            'id', 'unloading_station', 'due_time', 'weight',
            'missions'
        )

    def get_missions(self, instance):
        return OrderProductDeliverMissionSerializer(
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
    customer = ShortCustomerProfileSerializer(read_only=True)
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
            assignee: { id: '', name: '' },
            customer: { id: '', name: '' },
            due_time: due_time,
            loading_stations: [
                {
                    loading_station: { id: '', ... },
                    quality_station: { id: '', ... },
                    products: [
                        product: { id: '', ... },
                        total_weight: total_weight
                        unloading_stations: [
                            {
                                unloading_station: { id: '', ... }
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
        # check if assginee exists
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

        # check if customer exists
        customer_data = self.context.pop('customer', None)
        if customer_data is None:
            raise serializers.ValidationError({
                'customer': 'Customer data are missing'
            })

        try:
            customer = CustomerProfile.objects.get(
                id=customer_data.get('id', None)
            )
        except CustomerProfile.DoesNotExist:
            raise serializers.ValidationError({
                'customer': 'Such customer does not exist'
            })

        # check if order data exists in request
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
                if total_weight == 0:
                    raise serializers.ValidationError({
                        'total_weight': 'Product weight cannot be zero'
                    })

                for unloading_station_data in unloading_stations_data:
                    weight = float(unloading_station_data.get('weight', 0))
                    if weight == 0:
                        raise serializers.ValidationError({
                            'weight': 'Unloading station weight cannot be zero'
                        })
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
            # get loading station
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

            # get quality station
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

            # get products
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
                    station_data = unloading_station_data.pop(
                        'unloading_station'
                    )
                    if station_data is None:
                        raise serializers.ValidationError({
                            'unloading_station':
                            'Unloading Station data are missing'
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
            assignee: { id: '', name: '' },
            customer: { id: '', name: '' },
            due_time: due_time,
            loading_stations: [
                {
                    loading_station: { id: '', ... },
                    quality_station: { id: '', ... },
                    products: [
                        product: { id: '', ... },
                        total_weight: total_weight
                        unloading_stations: [
                            {
                                unloading_station: { id: '', ... }
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
        # check if assginee exists
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

        # check if customer exists
        customer_data = self.context.pop('customer', None)
        if customer_data is None:
            raise serializers.ValidationError({
                'customer': 'Customer data are missing'
            })

        try:
            customer = CustomerProfile.objects.get(
                id=customer_data.get('id', None)
            )
        except CustomerProfile.DoesNotExist:
            raise serializers.ValidationError({
                'customer': 'Such customer does not exist'
            })

        # check if order data exists in request
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
                if total_weight == 0:
                    raise serializers.ValidationError({
                        'total_weight': 'Product weight cannot be zero'
                    })

                for unloading_station_data in unloading_stations_data:
                    weight = float(unloading_station_data.get('weight', 0))
                    if weight == 0:
                        raise serializers.ValidationError({
                            'weight': 'Unloading station weight cannot be zero'
                        })
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
        # instance.loading_stations.clear()
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

            order_loading_station_id = loading_station_data.get(
                'id', None
            )

            if order_loading_station_id is None:
                order_loading_station = m.OrderLoadingStation.objects.create(
                    order=instance,
                    loading_station=loading_station,
                    quality_station=quality_station,
                    **loading_station_data
                )
            else:
                order_loading_station = get_object_or_404(
                    m.OrderLoadingStation,
                    id=loading_station_data.get('id', None)
                )
                order_loading_station.loading_station = loading_station
                order_loading_station.quality_station = quality_station
                for (key, value) in loading_station_data.items():
                    setattr(order_loading_station, key, value)

                order_loading_station.save()

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

                order_product_id = product_data.get('id', None)
                if order_product_id is None:
                    order_product = m.OrderProduct.objects.create(
                        order_loading_station=order_loading_station,
                        product=product,
                        **product_data
                    )
                else:
                    order_product = get_object_or_404(
                        m.OrderProduct,
                        id=product_data.get('id', None)
                    )
                    order_product.order_loading_station = order_loading_station
                    order_product.product = product
                    for (key, value) in product_data.items():
                        setattr(order_product, key, value)
                    order_product.save()

                for unloading_station_data in unloading_stations_data:
                    station_data = unloading_station_data.pop(
                        'unloading_station'
                    )
                    unloading_station_data.pop('missions', None)
                    if station_data is None:
                        raise serializers.ValidationError({
                            'unloading_station':
                            'Unloading Station data are missing'
                        })

                    unloading_station = Station.unloadingstations.get(
                        pk=station_data.get('id')
                    )

                    order_product_deliver_id = unloading_station_data.get(
                        'id', None
                    )
                    if order_product_deliver_id is None:
                        m.OrderProductDeliver.objects.create(
                            order_product=order_product,
                            unloading_station=unloading_station,
                            **unloading_station_data
                        )
                    else:
                        order_product_deliver = get_object_or_404(
                            m.OrderProductDeliver,
                            id=unloading_station_data.get('id', None)
                        )
                        order_product_deliver.order_product = order_product
                        order_product_deliver.unloading_station =\
                            unloading_station
                        for (key, value) in unloading_station_data.items():
                            setattr(order_product_deliver, key, value)

                        order_product_deliver.save()

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
    customer = ShortCustomerProfileSerializer(read_only=True)
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


class JobMileageField(serializers.Field):

    def to_representation(self, instance):
        return {
            'total_mileage': instance.total_mileage,
            'highway_mileage': instance.highway_mileage,
            'normalway_mileage': instance.normalway_mileage,
            'empty_mileage': instance.empty_mileage,
            'heavy_mileage':  instance.heavy_mileage
        }


class ShortJobSerializer(serializers.ModelSerializer):

    driver = ShortUserSerializer()
    escort = ShortUserSerializer()
    vehicle = ShortVehicleSerializer()
    route = ShortRouteSerializer()
    missions = ShortMissionSerializer(
        source='mission_set', many=True, read_only=True
    )

    mileage = JobMileageField(source='*')

    class Meta:
        model = m.Job
        fields = (
            'driver', 'escort', 'vehicle', 'missions', 'route', 'mileage'
        )


class JobSerializer(serializers.ModelSerializer):

    vehicle = serializers.CharField(source='vehicle.plate_num')
    driver = serializers.CharField(source='driver.name')
    escort = serializers.CharField(source='escort.name')
    loading_station = serializers.CharField(source='loading_station.name')
    quality_station = serializers.CharField(source='quality_station.name')
    unloading_stations = serializers.SerializerMethodField()
    mileage = JobMileageField(source='*')

    class Meta:
        model = m.Job
        fields = (
            'id', 'vehicle', 'driver', 'escort', 'loading_station',
            'quality_station', 'unloading_stations', 'mileage'
        )

    def get_unloading_stations(self, job):
        ret = []
        for station in job.unloading_stations:
            ret.append({
                'name': station.name
            })

        return ret


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

    class Meta:
        model = m.Job
        fields = (
            'id', 'vehicle', 'driver', 'escort', 'stations', 'products',
            'progress', 'progress_bar', 'total_weight',
            'start_due_time', 'finish_due_time', 'route'
        )


class JobProductSerializer(serializers.Serializer):

    name = serializers.CharField()
    mission_weight = serializers.FloatField()
    loading_weight = serializers.FloatField()
    unloading_weight = serializers.FloatField()


class JobCurrentSerializer(serializers.ModelSerializer):
    """
    Serializer for current job for driver app
    """
    plate_num = serializers.CharField(source='vehicle.plate_num')
    driver = serializers.CharField(source='driver.name')
    escort = serializers.CharField(source='escort.name')
    stations = serializers.SerializerMethodField()
    products = JobProductSerializer(many=True)
    progress_bar = JobProgressBarField(source='*')
    progress = serializers.SerializerMethodField()

    class Meta:
        model = m.Job
        fields = (
            'id', 'plate_num', 'driver', 'escort', 'stations',
            'products', 'total_weight',
            'progress', 'progress_bar', 'route'
        )

    def get_progress(self, instance):
        progress = instance.progress
        if progress == c.JOB_PROGRESS_NOT_STARTED:
            last_progress_finished_on = None

        if progress == c.JOB_PROGRESS_TO_LOADING_STATION:
            last_progress_finished_on = instance.started_on

        elif progress == c.JOB_PROGRESS_ARRIVED_AT_LOADING_STATION:
            last_progress_finished_on = instance.arrived_loading_station_on

        elif progress == c.JOB_PROGRESS_LOADING_AT_LOADING_STATION:
            last_progress_finished_on = instance.started_loading_on

        elif progress == c.JOB_PROGRESS_FINISH_LOADING_AT_LOADING_STATION:
            last_progress_finished_on = instance.finished_loading_on

        elif progress == c.JOB_PROGRESS_TO_QUALITY_STATION:
            last_progress_finished_on = instance.departure_loading_station_on

        elif progress == c.JOB_PROGRESS_ARRIVED_AT_QUALITY_STATION:
            last_progress_finished_on = instance.arrived_quality_station_on

        elif progress == c.JOB_PROGRESS_CHECKING_AT_QUALITY_STATION:
            last_progress_finished_on = instance.started_checking_on

        elif progress == c.JOB_PROGRESS_FINISH_CHECKING_AT_QUALITY_STATION:
            last_progress_finished_on = instance.finished_checking_on

        elif (progress - c.JOB_PROGRESS_TO_UNLOADING_STATION) >= 0:
            mission_step = (progress - c.JOB_PROGRESS_TO_UNLOADING_STATION) / 4
            us_progress = (progress - c.JOB_PROGRESS_TO_UNLOADING_STATION) % 4
            mission = instance.mission_set.get(step=mission_step)
            if us_progress == 0:
                last_progress_finished_on = mission.arrived_station_on
            elif us_progress == 1:
                last_progress_finished_on = mission.started_unloading_on
            elif us_progress == 2:
                last_progress_finished_on = mission.finished_unloading_on
            elif us_progress == 3:
                last_progress_finished_on = mission.departure_station_on

        return {
            'progress': progress,
            'last_progress_finished_on': last_progress_finished_on
        }

    def get_stations(self, job):
        ret = []
        ret.append({
            'name': job.loading_station.name,
            'products': job.products
        })
        ret.append({
            'name': job.quality_station.name,
            'products': job.products
        })
        for mission in job.mission_set.all():
            ret.append({
                'name': mission.mission.unloading_station.name,
                'products': [{
                    'name': mission.mission.order_product.product.name,
                    'mission_weight': mission.mission_weight,
                    'loading_weight': mission.loading_weight,
                    'unloading_weight': mission.unloading_weight
                }]
            })

        return ret


class JobFutureSerializer(serializers.ModelSerializer):
    """
    Serializer for future jobs in driver app
    """
    order_id = serializers.CharField(source='order.id')
    plate_num = serializers.CharField(source='vehicle.plate_num')
    stations = serializers.SerializerMethodField()

    class Meta:
        model = m.Job
        fields = (
            'id', 'order_id', 'plate_num', 'stations'
        )

    def get_stations(self, job):
        ret = []
        for station in job.stations:
            ret.append({
                'name': station.name
            })

        return ret


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
    Serializer for completed jobs in driver app
    """
    order_id = serializers.CharField(source='order.id')
    plate_num = serializers.CharField(source='vehicle.plate_num')
    stations = serializers.SerializerMethodField()
    products = JobProductSerializer(many=True)
    driver = serializers.CharField(source='driver.name')
    escort = serializers.CharField(source='escort.name')
    mileage = JobMileageField(source='*')
    bills = serializers.SerializerMethodField()

    class Meta:
        model = m.Job
        fields = (
            'id', 'order_id', 'plate_num', 'stations',
            'started_on', 'finished_on',
            'products', 'total_weight', 'driver', 'escort',
            'mileage', 'bills'
        )

    def get_stations(self, job):
        ret = []
        ret.append({
            'name': job.loading_station.name,
            'arrived_on': job.arrived_loading_station_on
        })
        ret.append({
            'name': job.quality_station.name,
            'arrived_on': job.arrived_quality_station_on
        })
        for mission in job.mission_set.all():
            ret.append({
                'name': mission.mission.unloading_station.name,
                'arrived_on': mission.arrived_station_on
            })

        return ret

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


class MissionTimeDurationSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Mission
        fields = (
            'rushing_time_to_unloading_station',
            'waiting_time_on_unloading_station',
            'unloading_time_on_unloading_station',
        )


class JobTimeDurationSerializer(serializers.ModelSerializer):
    """
    This serializer is used for displaying time duration
    """
    order = ShortOrderSerializer()
    vehicle = ShortVehicleSerializer()
    driver = ShortUserSerializer()
    escort = ShortUserSerializer()
    missions = MissionTimeDurationSerializer(many=True)

    class Meta:
        model = m.Job
        fields = (
            'id', 'order', 'vehicle', 'driver', 'escort',
            'total_time', 'rushing_time_to_loading_station',
            'waiting_time_on_loading_station',
            'loading_time_on_loading_station',
            'rushing_time_to_quality_station',
            'waiting_time_on_quality_station',
            'checking_time_on_quality_station',
            'missions'
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
