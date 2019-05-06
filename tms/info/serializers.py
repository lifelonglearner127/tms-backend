from rest_framework import serializers

from .models import (
    Product, LoadingStation, UnLoadingStation, QualityStation, OilStation
)


class ShortProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = (
            'id', 'name'
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

    product = ShortProductSerializer()

    class Meta:
        model = LoadingStation
        fields = '__all__'


class ShortUnLoadingStationSerializer(serializers.ModelSerializer):

    class Meta:
        model = UnLoadingStation
        fields = (
            'id', 'name', 'contact', 'mobile', 'address'
        )


class UnLoadingStationSerializer(serializers.ModelSerializer):

    product = ShortProductSerializer()

    class Meta:
        model = UnLoadingStation
        fields = '__all__'


class QualityStationSerializer(serializers.ModelSerializer):

    class Meta:
        model = QualityStation
        fields = '__all__'


class OilStationSerializer(serializers.ModelSerializer):

    class Meta:
        model = OilStation
        fields = '__all__'
