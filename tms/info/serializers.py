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


class LoadStationSerializer(serializers.ModelSerializer):
    """
    Serializer for short data of Load Station
    Used for base class for Loading, Unloading Station
    """
    def create(self, validated_data):
        product_data = self.context.get('product', None)
        if product_data is None:
            raise serializers.ValidationError('No product is provided')

        product_id = product_data.get('id', None)
        if product_id is None:
            raise serializers.ValidationError('Invalid product data structure')

        try:
            product = m.Product.objects.get(pk=product_id)
        except m.Product.DoesNotExist:
            raise serializers.ValidationError('Could not found such product')

        return self.Meta.model.objects.create(
            product=product, **validated_data
        )

    def update(self, instance, validated_data):
        product_data = self.context.get('product', None)
        if product_data is None:
            raise serializers.ValidationError('No product is provided')

        product_id = product_data.get('id', None)
        if product_id is None:
            raise serializers.ValidationError('Invalid product data structure')

        try:
            product = m.Product.objects.get(pk=product_id)
        except m.Product.DoesNotExist:
            raise serializers.ValidationError('Could not found such product')

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
        model = m.LoadingStation
        fields = (
            'id', 'name', 'contact', 'mobile', 'address'
        )


class LoadingStationSerializer(LoadStationSerializer):
    """
    Serializer for Loading Station
    """
    product = ShortProductSerializer(read_only=True)

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


class UnLoadingStationSerializer(LoadStationSerializer):
    """
    Serializer for UnLoading Station
    """
    product = ShortProductSerializer(read_only=True)

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
