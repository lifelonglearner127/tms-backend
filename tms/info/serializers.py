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


class ProductInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for Product
    """
    category = serializers.CharField(source='get_category_display')

    class Meta:
        model = m.Product
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product
    """
    class Meta:
        model = m.Product
        fields = '__all__'


class ShortStationSerializer(serializers.ModelSerializer):
    """
    Serializer for short data of Loading Station
    """
    class Meta:
        model = m.Station
        fields = (
            'id', 'name', 'contact', 'mobile', 'address'
        )


class StationInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for Loading Station
    """
    product_category = serializers.CharField(
        source='get_product_category_display'
    )

    class Meta:
        model = m.Station
        fields = '__all__'


class StationSerializer(serializers.ModelSerializer):
    """
    Serializer for Loading Station
    """
    class Meta:
        model = m.Station
        fields = '__all__'
