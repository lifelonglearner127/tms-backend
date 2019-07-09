from django.shortcuts import get_object_or_404

from rest_framework import serializers
from . import models as m
from ..core import constants as c
from ..core.serializers import TMSChoiceField


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
    weight_measure_unit = TMSChoiceField(choices=c.PRODUCT_WEIGHT_MEASURE_UNIT)

    class Meta:
        model = m.Product
        fields = (
            'id', 'name', 'price', 'weight_measure_unit'
        )


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product
    """
    category = TMSChoiceField(choices=c.PRODUCT_CATEGORY)
    weight_measure_unit = TMSChoiceField(choices=c.PRODUCT_WEIGHT_MEASURE_UNIT)

    class Meta:
        model = m.Product
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['price_display'] =\
            str(instance.price) + '元 / ' +\
            str(instance.unit_weight) +\
            str(instance.get_weight_measure_unit_display())

        return ret


class ShortStationSerializer(serializers.ModelSerializer):
    """
    Serializer for short data of Loading Station
    """
    class Meta:
        model = m.Station
        fields = (
            'id', 'name', 'contact', 'mobile', 'address'
        )


class ShortStationPointSerializer(serializers.ModelSerializer):

    lnglat = serializers.SerializerMethodField()

    class Meta:
        model = m.Station
        fields = (
            'lnglat',
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
        products = self.context.get('products', None)
        if products is None:
            raise serializers.ValidationError({
                'product': 'Product is missing'
            })

        station = m.Station.objects.create(
            **validated_data
        )

        for product in products:
            product = get_object_or_404(m.Product, id=product.get('id', None))
            station.products.add(product)

        return station

    def update(self, instance, validated_data):
        products = self.context.get('products', None)
        if products is None:
            raise serializers.ValidationError({
                'product': 'Product is missing'
            })

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.products.clear()
        for product in products:
            product = get_object_or_404(m.Product, id=product.get('id', None))
            instance.products.add(product)

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


class WorkStationSerializer(serializers.ModelSerializer):
    """
    Serializer for Loading Station, Unloading Station, Quality Station
    """
    products = ShortProductSerializer(many=True, read_only=True)

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


class BlackDotSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Station
        fields = (
            'id', 'name', 'longitude', 'latitude', 'radius'
        )
