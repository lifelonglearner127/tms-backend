from rest_framework import serializers

from . import models as m
from ..info.models import Station
from ..info.serializers import ShortStationSerializer, ShortProductSerializer
from ..account.serializers import (
    ShortCustomerProfileSerializer, ShortStaffProfileSerializer
)
from ..account.models import StaffProfile, CustomerProfile


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

    def create(self, validated_data):
        # get customer
        customer_data = self.context.pop('customer', None)
        if customer_data is None:
            raise serializers.ValidationError('Customer data is not provided')

        try:
            customer_id = customer_data.get('id', None)
            customer = CustomerProfile.objects.get(pk=customer_id)
        except CustomerProfile.DoesNotExist:
            raise serializers.ValidationError('Such customer does not exist')

        # get assignee
        assignee_data = self.context.pop('assignee', None)
        if assignee_data is None:
            raise serializers.ValidationError('Assignee data is not provided')

        try:
            assignee_id = assignee_data.get('id', None)
            assignee = StaffProfile.objects.get(pk=assignee_id)
        except StaffProfile.DoesNotExist:
            raise serializers.ValidationError('Such staff does not exist')

        order = m.Order.objects.create(
            customer=customer,
            assignee=assignee,
            **validated_data
        )

        # get loading stations
        loading_stations_data = self.context.pop('loading_stations', None)
        if loading_stations_data is None:
            raise serializers.ValidationError(
                'Loading station data are not provided'
            )

        for loading_station_data in loading_stations_data:
            products_data = loading_station_data.pop(
                'products', None
            )
            if products_data is None:
                raise serializers.ValidationError(
                    'Products data are not provided'
                )

            station_data = loading_station_data.pop(
                'loading_station', None
            )
            loading_station_id = station_data.get('id', None)

            station_data = loading_station_data.pop(
                'quality_station', None
            )
            quality_station_id = station_data.get('id', None)
            # select_object_or_404 can be used but I use try/catch for
            # rich error msg
            try:
                loading_station = Station.loading.get(
                    pk=loading_station_id
                )
                quality_station = Station.quality.get(
                    pk=quality_station_id
                )
                order_loading_station = m.OrderLoadingStation.objects.create(
                    order=order,
                    loading_station=loading_station,
                    quality_station=quality_station,
                    **loading_station_data
                )
            except Station.DoesNotExist:
                raise serializers.ValidationError(
                    'Such loading station does not exist'
                    )

            # get ordred products
            for product_data in products_data:
                # get ordered details of each products
                unloading_stations_data = product_data.pop(
                    'unloading_stations', None
                )
                if unloading_stations_data is None:
                    raise serializers.ValidationError(
                        'Unloading stations are not provided'
                        )

                try:
                    order_product_data = product_data.pop('product', None)
                    product_id = order_product_data.get('id', None)
                    product = m.Product.objects.get(pk=product_id)
                except m.Product.DoesNotExist:
                    raise serializers.ValidationError(
                        'Such product does not exist'
                        )

                order_product = m.OrderProduct.objects.create(
                    order_loading_station=order_loading_station,
                    product=product, **product_data
                )

                for unloading_station_data in unloading_stations_data:
                    # get unlaoding station
                    station_data = unloading_station_data.pop(
                        'unloading_station', None
                        )
                    if station_data is None:
                        raise serializers.ValidationError(
                            'Unloading station is not provided'
                        )

                    try:
                        station_id = station_data.get(
                            'id', None
                        )
                        unloading_station = Station.unloading.get(
                            pk=station_id
                        )
                    except Station.DoesNotExist:
                        raise serializers.ValidationError(
                            'Such unloading station does not exist'
                        )

                    m.OrderProductDeliver.objects.create(
                        order_product=order_product,
                        unloading_station=unloading_station,
                        **unloading_station_data
                    )

        return order

    def update(self, instance, validated_data):
        # get customer
        customer_data = self.context.pop('customer', None)
        if customer_data is None:
            raise serializers.ValidationError('Customer data is not provided')

        try:
            customer_id = customer_data.get('id', None)
            customer = CustomerProfile.objects.get(pk=customer_id)
        except CustomerProfile.DoesNotExist:
            raise serializers.ValidationError('Such customer does not exist')

        # get assignee
        assignee_data = self.context.pop('assignee', None)
        if assignee_data is None:
            raise serializers.ValidationError('Assignee data is not provided')

        try:
            assignee_id = assignee_data.get('id', None)
            assignee = StaffProfile.objects.get(pk=assignee_id)
        except StaffProfile.DoesNotExist:
            raise serializers.ValidationError('Such staff does not exist')

        instance.assignee = assignee
        instance.customer = customer

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        instance.loading_stations.clear()

        # get loading stations
        loading_stations_data = self.context.pop('loading_stations', None)
        if loading_stations_data is None:
            raise serializers.ValidationError(
                'Loading station data are not provided'
            )

        for loading_station_data in loading_stations_data:
            products_data = loading_station_data.pop(
                'products', None
            )
            if products_data is None:
                raise serializers.ValidationError(
                    'Products data are not provided'
                )

            # select_object_or_404 can be used but I use try/catch for
            # rich error msg
            try:
                station_data = loading_station_data.pop(
                    'loading_station', None
                )
                loading_station_id = station_data.get('id', None)
                loading_station = Station.loading.get(
                    pk=loading_station_id
                )

                station_data = loading_station_data.pop(
                    'quality_station', None
                )
                quality_station_id = station_data.get('id', None)
                quality_station = Station.quality.get(
                    pk=quality_station_id
                )
                order_loading_station = m.OrderLoadingStation.objects.create(
                    order=instance,
                    loading_station=loading_station,
                    quality_station=quality_station,
                    **loading_station_data
                )
            except Station.DoesNotExist:
                raise serializers.ValidationError(
                    'Such loading station does not exist'
                    )

            # get ordred products
            for product_data in products_data:
                # get ordered details of each products
                unloading_stations_data = product_data.pop(
                    'unloading_stations', None
                )
                if unloading_stations_data is None:
                    raise serializers.ValidationError(
                        'Unloading stations are not provided'
                        )

                try:
                    order_product_data = product_data.pop('product', None)
                    product_id = order_product_data.get('id', None)
                    product = m.Product.objects.get(pk=product_id)
                except m.Product.DoesNotExist:
                    raise serializers.ValidationError(
                        'Such product does not exist'
                        )

                order_product = m.OrderProduct.objects.create(
                    order_loading_station=order_loading_station,
                    product=product, **product_data
                )

                for unloading_station_data in unloading_stations_data:
                    # get unlaoding station
                    station_data = unloading_station_data.pop(
                        'unloading_station', None
                        )
                    if station_data is None:
                        raise serializers.ValidationError(
                            'Unloading station is not provided'
                        )

                    try:
                        station_id = station_data.get(
                            'id', None
                        )
                        unloading_station = Station.unloading.get(
                            pk=station_id
                        )
                    except Station.DoesNotExist:
                        raise serializers.ValidationError(
                            'Such unloading station does not exist'
                        )

                    m.OrderProductDeliver.objects.create(
                        order_product=order_product,
                        unloading_station=unloading_station,
                        **unloading_station_data
                    )

        return instance
