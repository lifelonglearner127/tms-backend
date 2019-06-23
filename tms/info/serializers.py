from rest_framework import serializers
from . import models as m
from ..core import constants as c
from ..core.serializers import TMSChoiceField


class ShortProductSerializer(serializers.ModelSerializer):
    """
    Serializer for short data of Product
    """
    class Meta:
        model = m.Product
        fields = (
            'id', 'name', 'price'
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
            str(instance.get_measure_unit_display())

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


class StationPointSerializer(serializers.ModelSerializer):

    lnglat = serializers.SerializerMethodField()

    class Meta:
        model = m.Station
        fields = (
            'lnglat',
        )

    def get_lnglat(self, obj):
        return [obj.longitude, obj.latitude]


class StationSerializer(serializers.ModelSerializer):
    """
    Serializer for Station
    """
    class Meta:
        model = m.Station
        fields = '__all__'


class WorkStationSerializer(serializers.ModelSerializer):
    """
    Serializer for Loading Station, Unloading Station, Quality Station
    """
    product_category = TMSChoiceField(c.PRODUCT_CATEGORY)

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
