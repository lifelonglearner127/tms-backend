from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import (
    Product, LoadingStation, UnLoadingStation, QualityStation, OilStation
)


class ShortProductSerializer(serializers.ModelSerializer):
    """
    Serializer for short data of Product
    """
    class Meta:
        model = Product
        fields = (
            'id', 'name', 'price'
        )


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product
    """
    class Meta:
        model = Product
        fields = '__all__'


class LoadStationSerializer(serializers.ModelSerializer):
    """
    Serializer for short data of Load Station
    Used for base class for Loading, Unloading Station
    """
    def create(self, validated_data):
        product_data = self.context.get('product')
        product_id = product_data.get('id')
        product = get_object_or_404(Product, pk=product_id)
        return self.Meta.model.objects.create(
            product=product, **validated_data
        )

    def update(self, instance, validated_data):
        product_data = self.context.get('product')
        product_id = product_data.get('id')
        product = get_object_or_404(Product, pk=product_id)

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.product = product
        instance.save()
        return instance


class ShortLoadingStationSerializer(serializers.ModelSerializer):
    """
    Serializer for short data of Loading Station
    """
    class Meta:
        model = LoadingStation
        fields = (
            'id', 'name', 'contact', 'mobile', 'address'
        )


class LoadingStationSerializer(LoadStationSerializer):
    """
    Serializer for Loading Station
    """
    product = ShortProductSerializer(read_only=True)

    class Meta:
        model = LoadingStation
        fields = '__all__'


class ShortUnLoadingStationSerializer(serializers.ModelSerializer):
    """
    Serializer for short data of UnLoading Station
    """
    class Meta:
        model = UnLoadingStation
        fields = (
            'id', 'name', 'contact', 'mobile', 'address'
        )


class UnLoadingStationSerializer(LoadStationSerializer):
    """
    Serializer for UnLoading Station
    """
    product = ShortProductSerializer(read_only=True)

    class Meta:
        model = UnLoadingStation
        fields = '__all__'


class ShortQualityStationSerializer(serializers.ModelSerializer):
    """
    Serializer for short data of Quality Station
    """
    class Meta:
        model = QualityStation
        fields = (
            'id', 'name', 'contact', 'mobile', 'address'
        )


class QualityStationSerializer(serializers.ModelSerializer):
    """
    Serializer for Quality Station
    """
    class Meta:
        model = QualityStation
        fields = '__all__'


class ShortOilStationSerializer(serializers.ModelSerializer):
    """
    Serializer for short data of Oil Station
    """
    class Meta:
        model = OilStation
        fields = (
            'id', 'name', 'contact', 'mobile', 'address'
        )


class OilStationSerializer(serializers.ModelSerializer):
    """
    Serializer for Oil Station
    """
    class Meta:
        model = OilStation
        fields = '__all__'
