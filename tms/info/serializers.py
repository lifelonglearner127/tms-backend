from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import (
    Product, LoadingStation, UnLoadingStation, QualityStation, OilStation
)


class ShortProductSerializer(serializers.ModelSerializer):

    value = serializers.CharField(source='id')
    text = serializers.CharField(source='name')

    class Meta:
        model = Product
        fields = (
            'value', 'text'
        )


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'


class ProductCategoriesSerializer(serializers.Serializer):

    value = serializers.CharField()
    text = serializers.CharField()


class ShortLoadingStationSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoadingStation
        fields = (
            'id', 'name', 'contact', 'mobile', 'address'
        )


class LoadingStationSerializer(serializers.ModelSerializer):

    product = ShortProductSerializer(read_only=True)

    class Meta:
        model = LoadingStation
        fields = '__all__'

    def create(self, validated_data):
        product_id = self.context.get('product_id')
        product = get_object_or_404(Product, pk=product_id)
        return LoadingStation.objects.create(
            product=product, **validated_data
        )

    def update(self, instance, validated_data):
        product_id = self.context.get('product_id')
        product = get_object_or_404(Product, pk=product_id)

        for (key, value) in validated_data.items():
            setattr(instance, key, value)
        
        instance.product = product
        instance.save()
        return instance

class ShortUnLoadingStationSerializer(serializers.ModelSerializer):

    class Meta:
        model = UnLoadingStation
        fields = (
            'id', 'name', 'contact', 'mobile', 'address'
        )


class UnLoadingStationSerializer(serializers.ModelSerializer):

    product = ShortProductSerializer(read_only=True)

    class Meta:
        model = UnLoadingStation
        fields = '__all__'

    def create(self, validated_data):
        product_id = self.context.get('product_id')
        product = get_object_or_404(Product, pk=product_id)
        return UnLoadingStation.objects.create(
            product=product, **validated_data
        )

    def update(self, instance, validated_data):
        product_id = self.context.get('product_id')
        product = get_object_or_404(Product, pk=product_id)

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.product = product
        instance.save()
        return instance


class QualityStationSerializer(serializers.ModelSerializer):

    class Meta:
        model = QualityStation
        fields = '__all__'


class OilStationSerializer(serializers.ModelSerializer):

    class Meta:
        model = OilStation
        fields = '__all__'
