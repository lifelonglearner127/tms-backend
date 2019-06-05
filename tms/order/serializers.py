from rest_framework import serializers

from . import models as m
from ..info.models import Station
from ..info.serializers import ShortStationSerializer, ShortProductSerializer
from ..account.serializers import (
    ShortCustomerProfileSerializer, ShortStaffProfileSerializer
)


class ShortOrderProductSerializer(serializers.ModelSerializer):

    product = ShortProductSerializer()

    class Meta:
        model = m.OrderProduct
        fields = (
            'product',
        )


class ShortOrderProductDeliverSerializer(serializers.ModelSerializer):

    unloading_station = ShortStationSerializer(
        read_only=True
    )

    order_product = ShortOrderProductSerializer(
        read_only=True
    )

    class Meta:
        model = m.OrderProductDeliver
        fields = (
            'id', 'unloading_station', 'order_product'
        )


class OrderProductDeliverSerializer(serializers.ModelSerializer):
    """
    Serializer for unloading stations selected for product delivery
    """
    unloading_station = ShortStationSerializer(
        read_only=True
    )

    class Meta:
        model = m.OrderProductDeliver
        fields = (
            'id', 'weight', 'unloading_station'
        )


class OrderProductSerializer(serializers.ModelSerializer):
    """
    Serializer for ordred products
    """
    unloading_stations = OrderProductDeliverSerializer(
        source='orderproductdeliver_set', many=True, read_only=True
    )

    product = ShortProductSerializer(read_only=True)

    class Meta:
        model = m.OrderProduct
        fields = (
            'id', 'product', 'total_weight', 'unloading_stations'
        )


class OrderLoadingStationSerializer(serializers.ModelSerializer):
    """
    Serializer for ordred loading statins
    """
    loading_station = ShortStationSerializer(read_only=True)
    quality_station = ShortStationSerializer(read_only=True)
    products = OrderProductSerializer(
        source='orderproduct_set', many=True, read_only=True
    )

    class Meta:
        model = m.OrderLoadingStation
        fields = (
            'id', 'loading_station', 'quality_station', 'due_time', 'products'
        )


class ShortOrderLoadingStationSerializer(serializers.ModelSerializer):

    loading_station = ShortStationSerializer(read_only=True)
    quality_station = ShortStationSerializer(read_only=True)

    class Meta:
        model = m.OrderLoadingStation
        fields = (
            'loading_station', 'quality_station'
        )


class OrderCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Order Create and Update Serializer
    """

    class Meta:
        model = m.Order
        fields = '__all__'

    def create(self, validated_data):
        """
        Request format
        {
            alias: alias,
            assignee: assignee_id,
            customer: customer_id,
            loading_stations:[
                {
                    loading_station: station_id,
                    quality_station: station_id,
                    due_time: due_time,
                    products: [
                        product: product_id,
                        total_weight: total_weight
                        unloading_stations: [
                            {
                                unloading_station: station_id
                                weight: weight
                            }
                        ]
                    ]
                }
            ]
        }
        1. Validate the data
        2. save models

        Cannot use validate_<field> or validate because we need to
           write writable nested serializer

        todo: remove twice db get; one for validation, other for saving models
        """
        # 1. Validate the data
        # get loading stations data
        loading_stations_data = self.context.pop('loading_stations', None)
        if loading_stations_data is None:
            raise serializers.ValidationError(
                'Loading station data are not provided'
            )

        for loading_station_data in loading_stations_data:
            products_data = loading_station_data.get(
                'products', None
            )
            if products_data is None:
                raise serializers.ValidationError(
                    'Products data are not provided'
                )

            # select_object_or_404 can be used but I use try/catch for
            # rich error msg
            try:
                # check loading station existence
                loading_station_id = loading_station_data.get(
                    'loading_station',
                    None
                )
                loading_station = Station.loading.get(
                    pk=loading_station_id
                )

                # check quality station existence
                quality_station_id = loading_station_data.get(
                    'quality_station', None
                )
                quality_station = Station.quality.get(
                    pk=quality_station_id
                )

            except Station.DoesNotExist:
                raise serializers.ValidationError(
                    'Such station does not exist'
                )

            # get ordred products
            for product_data in products_data:
                # get ordered details of each products
                unloading_stations_data = product_data.get(
                    'unloading_stations', None
                )
                if unloading_stations_data is None:
                    raise serializers.ValidationError(
                        'Unloading stations are not provided'
                    )

                try:
                    # check product existence
                    product_id = product_data.get('product', None)
                    product = m.Product.objects.get(pk=product_id)

                except m.Product.DoesNotExist:
                    raise serializers.ValidationError(
                        'Such product does not exist'
                    )

                total_weight = product_data.get('total_weight', 0)
                total_weight = int(total_weight)
                if total_weight == 0:
                    raise serializers.ValidationError(
                        'Improperly weight set'
                    )

                for unloading_station_data in unloading_stations_data:
                    # get unlaoding station
                    try:
                        unloading_station_id = unloading_station_data.get(
                            'unloading_station', None
                        )
                        unloading_station = Station.unloading.get(
                            pk=unloading_station_id
                        )
                        weight = unloading_station_data.get('weight', 0)
                        weight = int(weight)
                        if weight == 0:
                            raise serializers.ValidationError(
                                'Improperly weight set'
                            )
                        total_weight = total_weight - weight
                    except Station.DoesNotExist:
                        raise serializers.ValidationError(
                            'Such unloading station does not exist'
                        )

                if total_weight != 0:
                    raise serializers.ValidationError(
                        'Error occured while setting weights'
                    )

        # 2. save models
        order = m.Order.objects.create(
            **validated_data
        )

        for loading_station_data in loading_stations_data:
            loading_station = Station.loading.get(
                pk=loading_station_data.pop('loading_station')
            )
            quality_station = Station.quality.get(
                pk=loading_station_data.pop('quality_station')
            )
            products_data = loading_station_data.pop('products')

            order_loading_station = m.OrderLoadingStation.objects.create(
                order=order,
                loading_station=loading_station,
                quality_station=quality_station,
                **loading_station_data
            )

            for product_data in products_data:
                product = m.Product.objects.get(
                    pk=product_data.pop('product')
                )

                unloading_stations_data = product_data.pop(
                    'unloading_stations'
                )

                order_product = m.OrderProduct.objects.create(
                    order_loading_station=order_loading_station,
                    product=product, **product_data
                )

                for unloading_station_data in unloading_stations_data:
                    unloading_station = Station.unloading.get(
                        pk=unloading_station_data.pop('unloading_station')
                    )
                    m.OrderProductDeliver.objects.create(
                        order_product=order_product,
                        unloading_station=unloading_station,
                        **unloading_station_data
                    )

        return order

    def update(self, instance, validated_data):
        """
        Request format
        {
            alias: alias,
            assignee: assignee_id,
            customer: customer_id,
            loading_stations:[
                {
                    loading_station: station_id,
                    quality_station: station_id,
                    due_time: due_time,
                    products: [
                        product: product_id,
                        total_weight: total_weight
                        unloading_stations: [
                            {
                                unloading_station: station_id
                                weight: weight
                            }
                        ]
                    ]
                }
            ]
        }
        1. Validate the data
        2. save models

        Cannot use validate_<field> or validate because we need to
           write writable nested serializer

        todo: remove twice db get; one for validation, other for saving models
        """
        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        instance.loading_stations.clear()

        loading_stations_data = self.context.pop('loading_stations', None)
        if loading_stations_data is None:
            raise serializers.ValidationError(
                'Loading station data are not provided'
            )

        for loading_station_data in loading_stations_data:
            products_data = loading_station_data.get(
                'products', None
            )
            if products_data is None:
                raise serializers.ValidationError(
                    'Products data are not provided'
                )

            # select_object_or_404 can be used but I use try/catch for
            # rich error msg
            try:
                # check loading station existence
                loading_station_id = loading_station_data.get(
                    'loading_station',
                    None
                )
                loading_station = Station.loading.get(
                    pk=loading_station_id
                )

                # check quality station existence
                quality_station_id = loading_station_data.get(
                    'quality_station', None
                )
                quality_station = Station.quality.get(
                    pk=quality_station_id
                )

            except Station.DoesNotExist:
                raise serializers.ValidationError(
                    'Such station does not exist'
                )

            # get ordred products
            for product_data in products_data:
                # get ordered details of each products
                unloading_stations_data = product_data.get(
                    'unloading_stations', None
                )
                if unloading_stations_data is None:
                    raise serializers.ValidationError(
                        'Unloading stations are not provided'
                    )

                try:
                    # check product existence
                    product_id = product_data.get('product', None)
                    product = m.Product.objects.get(pk=product_id)

                except m.Product.DoesNotExist:
                    raise serializers.ValidationError(
                        'Such product does not exist'
                    )

                total_weight = product_data.get('total_weight', 0)
                total_weight = int(total_weight)
                if total_weight == 0:
                    raise serializers.ValidationError(
                        'Improperly weight set'
                    )

                for unloading_station_data in unloading_stations_data:
                    # get unlaoding station
                    try:
                        unloading_station_id = unloading_station_data.get(
                            'unloading_station', None
                        )
                        unloading_station = Station.unloading.get(
                            pk=unloading_station_id
                        )
                        weight = unloading_station_data.get('weight', 0)
                        weight = int(weight)
                        if weight == 0:
                            raise serializers.ValidationError(
                                'Improperly weight set'
                            )
                        total_weight = total_weight - weight
                    except Station.DoesNotExist:
                        raise serializers.ValidationError(
                            'Such unloading station does not exist'
                        )

                if total_weight != 0:
                    raise serializers.ValidationError(
                        'Error occured while setting weights'
                    )

        for loading_station_data in loading_stations_data:
            loading_station = Station.loading.get(
                pk=loading_station_data.pop('loading_station')
            )
            quality_station = Station.quality.get(
                pk=loading_station_data.pop('quality_station')
            )
            products_data = loading_station_data.pop('products')

            order_loading_station = m.OrderLoadingStation.objects.create(
                order=instance,
                loading_station=loading_station,
                quality_station=quality_station,
                **loading_station_data
            )

            for product_data in products_data:
                product = m.Product.objects.get(
                    pk=product_data.pop('product')
                )

                unloading_stations_data = product_data.pop(
                    'unloading_stations'
                )

                order_product = m.OrderProduct.objects.create(
                    order_loading_station=order_loading_station,
                    product=product, **product_data
                )

                for unloading_station_data in unloading_stations_data:
                    unloading_station = Station.unloading.get(
                        pk=unloading_station_data.pop('unloading_station')
                    )
                    m.OrderProductDeliver.objects.create(
                        order_product=order_product,
                        unloading_station=unloading_station,
                        **unloading_station_data
                    )
        return instance


class OrderSerializer(serializers.ModelSerializer):
    """
    Order serializer
    """
    loading_stations = OrderLoadingStationSerializer(
        source='orderloadingstation_set', many=True, read_only=True
    )

    assignee = ShortStaffProfileSerializer(read_only=True)
    customer = ShortCustomerProfileSerializer(read_only=True)

    class Meta:
        model = m.Order
        fields = '__all__'
