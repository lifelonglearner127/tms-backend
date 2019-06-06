from rest_framework import serializers
from . import models as m


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
    class Meta:
        model = m.Product
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['category_name'] = instance.get_category_display()

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


class WorkStationSerializer(serializers.ModelSerializer):
    """
    Serializer for Loading Station, Unloading Station, Quality Station
    """
    product_category_name = serializers.CharField(
        source='get_product_category_display', read_only=True
    )
    working_time_display = serializers.SerializerMethodField()
    average_time_display = serializers.SerializerMethodField()

    class Meta:
        model = m.Station
        fields = (
            'id', 'name', 'contact', 'mobile', 'address',
            'longitude', 'latitude', 'radius', 'product_category',
            'price', 'working_time', 'working_time_measure_unit',
            'average_time', 'average_time_measure_unit',
            'product_category_name', 'working_time_display',
            'average_time_display'
        )

    def get_working_time_display(self, instance):
        return str(instance.price) + '元/' + str(instance.working_time) +\
            str(instance.get_working_time_measure_unit_display())

    def get_average_time_display(self, instance):
        return str(instance.average_time) +\
            str(instance.get_average_time_measure_unit_display())


class OilStationSerializer(serializers.ModelSerializer):
    """
    Serializer for Oil Station
    """
    price_vary_display = serializers.SerializerMethodField()

    class Meta:
        model = m.Station
        fields = (
            'id', 'name', 'contact', 'mobile', 'address',
            'longitude', 'latitude', 'radius', 'price',
            'price_vary_duration', 'price_vary_duration_unit',
            'price_vary_display'
        )

    def get_price_vary_display(self, instance):
        return str(instance.price_vary_duration) + '个' +\
            str(instance.get_price_vary_duration_unit_display())
