from django.shortcuts import get_object_or_404

from rest_framework import serializers
from ..core import constants as c

# models
from . import models as m
from ..hr.models import CustomerProfile

# serializers
from ..core.serializers import TMSChoiceField
from ..hr.serializers import ShortCustomerProfileSerializer


class ShortProductDisplaySerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Product
        fields = (
            'name',
        )


class ShortProductSerializer(serializers.ModelSerializer):
    """
    Serializer for short data of Product
    """
    class Meta:
        model = m.Product
        fields = (
            'id', 'name'
        )


class ShortProductCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = m.ProductCategory
        fields = (
            'id', 'name'
        )


class ProductCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = m.ProductCategory
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product
    """
    category = ProductCategorySerializer(read_only=True)
    weight_measure_unit = TMSChoiceField(choices=c.PRODUCT_WEIGHT_MEASURE_UNIT)

    class Meta:
        model = m.Product
        fields = '__all__'

    def create(self, validated_data):
        category_data = self.context.get('category')
        if category_data is None:
            raise serializers.ValidationError({
                'category': 'Category data is missing'
            })
        try:
            category = m.ProductCategory.objects.get(
                id=category_data.get('id', None)
            )
        except m.ProductCategory.DoesNotExist:
            raise serializers.ValidationError({
                'category': 'Such category does not exist'
            })

        return m.Product.objects.create(
            category=category,
            **validated_data
        )

    def update(self, instance, validated_data):
        category_data = self.context.get('category')
        if category_data is None:
            raise serializers.ValidationError({
                'category': 'Category data is missing'
            })
        try:
            category = m.ProductCategory.objects.get(
                id=category_data.get('id', None)
            )
        except m.ProductCategory.DoesNotExist:
            raise serializers.ValidationError({
                'category': 'Such category does not exist'
            })

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.category = category
        instance.save()
        return instance

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['price_display'] =\
            str(instance.price) + '元 / ' +\
            str(instance.unit_weight) +\
            str(instance.get_weight_measure_unit_display())

        return ret


class AlarmSettingSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.AlarmSetting
        fields = '__all__'


class StationNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Station
        fields = (
            'id', 'name'
        )


class ShortStationSerializer(serializers.ModelSerializer):
    """
    Serializer for short data of Loading Station
    """
    class Meta:
        model = m.Station
        fields = (
            'id', 'name', 'contact', 'mobile', 'address', 'station_type'
        )


class ShortStationPointSerializer(serializers.ModelSerializer):

    lnglat = serializers.SerializerMethodField()

    class Meta:
        model = m.Station
        fields = (
            'lnglat', 'station_type'
        )

    def get_lnglat(self, obj):
        return [obj.longitude, obj.latitude]


class StationPointSerializer(serializers.ModelSerializer):

    lnglat = serializers.SerializerMethodField()

    class Meta:
        model = m.Station
        fields = (
            'id', 'name', 'station_type', 'lnglat',
        )

    def get_lnglat(self, obj):
        return [obj.longitude, obj.latitude]


class StationSerializer(serializers.ModelSerializer):
    """
    Serializer for Station
    """
    products = ShortProductSerializer(many=True, read_only=True)
    customers = ShortCustomerProfileSerializer(many=True, read_only=True)
    working_time_measure_unit = TMSChoiceField(
        choices=c.TIME_MEASURE_UNIT, required=False
    )
    average_time_measure_unit = TMSChoiceField(
        choices=c.TIME_MEASURE_UNIT, required=False
    )
    price_vary_duration_unit = TMSChoiceField(
        choices=c.PRICE_VARY_DURATION_UNIT, required=False
    )

    class Meta:
        model = m.Station
        fields = '__all__'

    def create(self, validated_data):
        products = self.context.get('products', [])
        customers = self.context.get('customers', [])
        station_type = validated_data.get('station_type', None)

        # validation if the station name exists already
        name = validated_data.get('name', None)
        if m.Station.objects.filter(
            station_type=station_type, name=name
        ).exists():
            raise serializers.ValidationError({
                'name': 'Already existts'
            })

        if station_type == c.STATION_TYPE_LOADING_STATION and len(products) == 0:
            raise serializers.ValidationError({
                'product': 'Product data is missing'
            })

        if station_type == c.STATION_TYPE_UNLOADING_STATION and len(customers) == 0:
            raise serializers.ValidationError({
                'customer': 'Customer data is missing'
            })

        station = m.Station.objects.create(
            **validated_data
        )

        for product in products:
            product = get_object_or_404(
                m.Product, id=product.get('id', None)
            )
            station.products.add(product)

        for customer in customers:
            customer = get_object_or_404(
                m.CustomerProfile, id=customer.get('id', None)
            )
            station.customers.add(customer)

        return station

    def update(self, instance, validated_data):
        products = self.context.get('products', [])
        customers = self.context.get('customer', [])
        station_type = validated_data.get('station_type', None)

        # validation if the station name exists already
        name = validated_data.get('name', None)
        if m.Station.objects.exclude(id=instance.id).filter(
            station_type=station_type, name=name
        ).exists():
            raise serializers.ValidationError({
                'name': 'Already existts'
            })

        if station_type == c.STATION_TYPE_LOADING_STATION and len(products) == 0:
            raise serializers.ValidationError({
                'product': 'Product data is missing'
            })

        if station_type == c.STATION_TYPE_UNLOADING_STATION and len(customers) == 0:
            raise serializers.ValidationError({
                'customer': 'Customer data is missing'
            })

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.products.clear()
        for product in products:
            product = get_object_or_404(
                m.Product, id=product.get('id', None)
            )
            instance.products.add(product)

        instance.customers.clear()
        for customer in customers:
            customer = get_object_or_404(
                m.CustomerProfile, id=customer.get('id', None)
            )
            instance.customers.add(customer)

        instance.save()
        return instance


class WorkStationSerializer(serializers.ModelSerializer):
    """
    Serializer for Loading Station, Unloading Station, Quality Station
    """
    products = ShortProductSerializer(many=True, read_only=True)
    customers = ShortCustomerProfileSerializer(many=True, read_only=True)

    class Meta:
        model = m.Station
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        ret['working_time_display'] =\
            str(instance.price) + '元/' +\
            str(instance.working_time) +\
            str(instance.get_working_time_measure_unit_display())

        ret['average_time_display'] =\
            str(instance.average_time) +\
            str(instance.get_average_time_measure_unit_display())

        return ret


class OilStationSerializer(serializers.ModelSerializer):
    """
    Serializer for Oil Station
    """
    class Meta:
        model = m.Station
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['price_vary_display'] = str(instance.price_vary_duration) +\
            '个' + str(instance.get_price_vary_duration_unit_display())

        return ret


class MainStationSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Station
        fields = (
            'id', 'name', 'longitude', 'latitude', 'radius'
        )


class BlackDotSerializer(MainStationSerializer):
    pass


class ParkingStationSerializer(MainStationSerializer):
    pass


class ShortRouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Route
        fields = (
            'id', 'name'
        )


class PathStationNameField(serializers.ListField):

    def to_representation(self, value):
        paths = m.Station.objects.filter(id__in=value)
        paths = dict([(point.id, point) for point in paths])

        serializer = StationPointSerializer(
            [paths[id] for id in value],
            many=True
        )
        return serializer.data


class RouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Route
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        paths = m.Station.objects.filter(id__in=ret['path'])
        paths = dict([(point.id, point) for point in paths])

        ret['path'] = StationPointSerializer(
            [paths[id] for id in paths],
            many=True
        ).data

        return ret


class PathLngLatField(serializers.ListField):

    def to_representation(self, value):
        paths = m.Station.objects.filter(id__in=value)
        paths = dict([(point.id, point) for point in paths])

        serializer = ShortStationPointSerializer(
            [paths[id] for id in value],
            many=True
        )
        return serializer.data


class RoutePointSerializer(serializers.ModelSerializer):

    path = PathLngLatField()

    class Meta:
        model = m.Route
        fields = (
            'id', 'path'
        )


class TransportationDistanceSerializer(serializers.ModelSerializer):

    start_point = ShortStationSerializer(read_only=True)
    end_point = ShortStationSerializer(read_only=True)

    class Meta:
        model = m.TransportationDistance
        fields = '__all__'

    def create(self, validated_data):
        start_point_data = self.context.get('start_point')
        if start_point_data is None:
            raise serializers.ValidationError({
                'start_point': 'Start point data is missing'
            })
        try:
            start_point = m.Station.objects.get(
                id=start_point_data.get('id', None)
            )
        except m.Station.DoesNotExist:
            raise serializers.ValidationError({
                'start_point': 'Such station data does not exist'
            })

        end_point_data = self.context.get('end_point')
        if end_point_data is None:
            raise serializers.ValidationError({
                'end_point': 'End point data is missing'
            })
        try:
            end_point = m.Station.objects.get(
                id=end_point_data.get('id', None)
            )
        except m.Station.DoesNotExist:
            raise serializers.ValidationError({
                'end_point': 'Such station data does not exist'
            })

        return m.TransportationDistance.objects.create(
            start_point=start_point,
            end_point=end_point,
            **validated_data
        )

    def update(self, instance, validated_data):
        start_point_data = self.context.get('start_point')
        if start_point_data is None:
            raise serializers.ValidationError({
                'start_point': 'Start point data is missing'
            })
        try:
            start_point = m.Station.objects.get(
                id=start_point_data.get('id', None)
            )
        except m.Station.DoesNotExist:
            raise serializers.ValidationError({
                'start_point': 'Such station data does not exist'
            })

        end_point_data = self.context.get('end_point')
        if end_point_data is None:
            raise serializers.ValidationError({
                'end_point': 'End point data is missing'
            })
        try:
            end_point = m.Station.objects.get(
                id=end_point_data.get('id', None)
            )
        except m.Station.DoesNotExist:
            raise serializers.ValidationError({
                'end_point': 'Such station data does not exist'
            })

        instance.start_point = start_point
        instance.end_point = end_point

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance
