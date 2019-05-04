from django.shortcuts import get_object_or_404

from rest_framework import serializers

from .models import Order, OrderProduct, OrderProductDeliver
from ..info.models import Product, UnLoadingStation, LoadingStation
from ..info.serializers import (
    ShortUnLoadingStationSerializer, ShortLoadingStationSerializer,
    ShortProductSerializer
)


class OrderProductDeliverSerializer(serializers.ModelSerializer):

    unloading_station = ShortUnLoadingStationSerializer(
        read_only=True
    )

    class Meta:
        model = OrderProductDeliver
        fields = (
            'weight', 'unloading_station',
        )


class OrderProductSerializer(serializers.ModelSerializer):

    unloading_stations = OrderProductDeliverSerializer(
        source='orderproductdeliver_set', many=True, read_only=True
    )

    product = ShortProductSerializer(read_only=True)

    class Meta:
        model = OrderProduct
        fields = (
            'product', 'total_weight', 'unloading_stations'
        )


class OrderSerializer(serializers.ModelSerializer):

    products = OrderProductSerializer(
        source='orderproduct_set', many=True, read_only=True
    )

    loading_station = ShortLoadingStationSerializer(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):

        loading_station_data = self.context.get('loading_station', None)
        loading_station_id = loading_station_data.get('id', None)
        loading_station = get_object_or_404(
            LoadingStation, pk=loading_station_id
        )

        order = Order.objects.create(
            loading_station=loading_station,
            **validated_data
        )

        products_delivers = self.context.get('products', [])

        for product_deliver in products_delivers:
            unloading_stations_delivers = product_deliver.pop(
                'unloading_stations', None
            )
            product_data = product_deliver.pop('product', None)
            product_id = product_data.get('id', None)
            product = get_object_or_404(Product, pk=product_id)
            order_product = OrderProduct.objects.create(
                order=order, product=product, **product_deliver
            )
            for unloading_station_deliver in unloading_stations_delivers:
                unloading_station_data = unloading_station_deliver.pop(
                    'unloading_station', None
                    )
                unloading_station_id = unloading_station_data.get('id', None)
                unloading_station = get_object_or_404(
                    UnLoadingStation, pk=unloading_station_id
                )
                OrderProductDeliver.objects.create(
                    order_product=order_product,
                    unloading_station=unloading_station,
                    **unloading_station_deliver
                )

        return order
