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


class ShortLoadingStationSerializer(serializers.ModelSerializer):
    """
    Serializer for short data of Loading Station
    """
    class Meta:
        model = m.LoadingStation
        fields = (
            'id', 'name', 'contact', 'mobile', 'address'
        )


class LoadingStationInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for Loading Station
    """
    product_category = serializers.CharField(
        source='get_product_category_display'
    )

    class Meta:
        model = m.LoadingStation
        fields = '__all__'


class LoadingStationSerializer(serializers.ModelSerializer):
    """
    Serializer for Loading Station
    """
    class Meta:
        model = m.LoadingStation
        fields = '__all__'


class ShortUnLoadingStationSerializer(serializers.ModelSerializer):
    """
    Serializer for short data of UnLoading Station
    """
    class Meta:
        model = m.UnLoadingStation
        fields = (
            'id', 'name', 'contact', 'mobile', 'address'
        )


class UnLoadingStationInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for UnLoading Station
    """
    product_category = serializers.CharField(
        source='get_product_category_display'
    )

    class Meta:
        model = m.UnLoadingStation
        fields = '__all__'


class UnLoadingStationSerializer(serializers.ModelSerializer):
    """
    Serializer for UnLoading Station
    """
    class Meta:
        model = m.UnLoadingStation
        fields = '__all__'


class ShortQualityStationSerializer(serializers.ModelSerializer):
    """
    Serializer for short data of Quality Station
    """
    class Meta:
        model = m.QualityStation
        fields = (
            'id', 'name', 'contact', 'mobile', 'address'
        )


class QualityStationSerializer(serializers.ModelSerializer):
    """
    Serializer for Quality Station
    """
    class Meta:
        model = m.QualityStation
        fields = '__all__'


class ShortOilStationSerializer(serializers.ModelSerializer):
    """
    Serializer for short data of Oil Station
    """
    class Meta:
        model = m.OilStation
        fields = (
            'id', 'name', 'contact', 'mobile', 'address'
        )


class OilStationSerializer(serializers.ModelSerializer):
    """
    Serializer for Oil Station
    """
    class Meta:
        model = m.OilStation
        fields = '__all__'
