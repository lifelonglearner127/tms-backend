from rest_framework import serializers

from . import models as m
from ..core import constants as c
from ..core.serializers import TMSChoiceField
from ..account.serializers import ShortUserSerializer
from ..info.models import Station
from ..info.serializers import ShortStationSerializer, ShortProductSerializer


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
        exclude = (
            'order_product',
        )


class OrderProductSerializer(serializers.ModelSerializer):
    """
    Serializer for ordred products
    """
    unloading_stations = OrderProductDeliverSerializer(
        source='orderproductdeliver_set', many=True, read_only=True
    )

    product = ShortProductSerializer(read_only=True)
    total_weight_measure_unit = TMSChoiceField(
        choices=c.PRODUCT_WEIGHT_MEASURE_UNIT
    )
    price_weight_measure_unit = TMSChoiceField(
        choices=c.PRODUCT_WEIGHT_MEASURE_UNIT
    )
    loss_unit = TMSChoiceField(
        choices=c.PRODUCT_WEIGHT_MEASURE_UNIT
    )
    payment_method = TMSChoiceField(
        choices=c.PAYMENT_METHOD
    )

    class Meta:
        model = m.OrderProduct
        exclude = (
            'order_loading_station',
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
        exclude = (
            'order',
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
    Order Create and Update Serializer
    """
    assignee = ShortUserSerializer(read_only=True)
    customer = ShortUserSerializer(read_only=True)
    order_source = TMSChoiceField(choices=c.ORDER_SOURCE, required=False)
    status = TMSChoiceField(choices=c.ORDER_STATUS, required=False)
    loading_stations = OrderLoadingStationSerializer(
        source='orderloadingstation_set', many=True, read_only=True
    )

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
            due_time: due_time,
            loading_stations: [
                {
                    loading_station: station_id,
                    quality_station: station_id,
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
        assignee_data = self.context.pop('assignee', None)
        if assignee_data is None:
            raise serializers.ValidationError({
                'assignee': 'Assignee data are missing'
            })

        try:
            assignee = m.User.objects.get(id=assignee_data.get('id', None))
        except m.User.DoesNotExist:
            raise serializers.ValidationError({
                'assignee': 'Such user does not exist'
            })

        customer_data = self.context.pop('customer', None)
        if customer_data is None:
            raise serializers.ValidationError({
                'customer': 'Customer data are missing'
            })

        try:
            customer = m.User.objects.get(id=customer_data.get('id', None))
        except m.User.DoesNotExist:
            raise serializers.ValidationError({
                'customer': 'Such customer does not exist'
            })

        loading_stations_data = self.context.pop('loading_stations', None)
        weight_errors = []
        if loading_stations_data is None:
            raise serializers.ValidationError({
                'order': 'Order data are missing'
            })

        for loading_station_data in loading_stations_data:
            products_data = loading_station_data.get(
                'products', None
            )
            if products_data is None:
                raise serializers.ValidationError({
                    'products': 'Order Product data are missing'
                })

            # validate product weights
            product_index = 0
            for product_data in products_data:
                unloading_stations_data = product_data.get(
                    'unloading_stations', None
                )
                if unloading_stations_data is None:
                    raise serializers.ValidationError({
                        'unloading_station':
                        'Unloading stations are not provided'
                    })
                total_weight = float(product_data.get('total_weight', 0))
                total_weight = float(total_weight)
                # TODO: check total weight validation

                for unloading_station_data in unloading_stations_data:
                    # TODO: check unloading station weight validation
                    weight = float(unloading_station_data.get('weight', 0))
                    total_weight = total_weight - weight

                if total_weight != 0:
                    weight_errors.append(product_index)
                product_index = product_index + 1

        if weight_errors:
            raise serializers.ValidationError({
                'weight': weight_errors
            })
        # 2. save models
        order = m.Order.objects.create(
            assignee=assignee,
            customer=customer,
            **validated_data
        )

        for loading_station_data in loading_stations_data:
            station_data = loading_station_data.pop('loading_station')
            if station_data is None:
                raise serializers.ValidationError({
                    'loading_station': 'Loading Station data are missing'
                })

            try:
                loading_station = Station.loadingstations.get(
                    id=station_data.get('id', None)
                )
            except Station.DoesNotExist:
                raise serializers.ValidationError({
                    'loading_station': 'Loading Station does not exists'
                })

            station_data = loading_station_data.pop('quality_station')
            if station_data is None:
                raise serializers.ValidationError({
                    'quality_station': 'Quality Station data are missing'
                })
            try:
                quality_station = Station.qualitystations.get(
                    pk=station_data.get('id')
                )
            except Station.DoesNotExist:
                raise serializers.ValidationError({
                    'quality_station': 'Quality Station does not exists'
                })

            products_data = loading_station_data.pop('products')

            order_loading_station = m.OrderLoadingStation.objects.create(
                order=order,
                loading_station=loading_station,
                quality_station=quality_station,
                **loading_station_data
            )

            for product_data in products_data:
                product = product_data.pop('product', None)
                if product is None:
                    raise serializers.ValidationError({
                        'product': 'Product data are missing'
                    })

                try:
                    product = m.Product.objects.get(
                        id=product.get('id')
                    )
                except m.Product.DoesNotExist:
                    raise serializers.ValidationError({
                        'product': 'Product does not exist'
                    })

                unloading_stations_data = product_data.pop(
                    'unloading_stations'
                )

                product_data['total_weight_measure_unit'] =\
                    product_data['total_weight_measure_unit']['value']
                product_data['price_weight_measure_unit'] =\
                    product_data['price_weight_measure_unit']['value']
                product_data['loss_unit'] =\
                    product_data['loss_unit']['value']
                product_data['payment_method'] =\
                    product_data['payment_method']['value']
                order_product = m.OrderProduct.objects.create(
                    order_loading_station=order_loading_station,
                    product=product,
                    **product_data
                )

                for unloading_station_data in unloading_stations_data:
                    station_data = unloading_station_data.pop('unloading_station')
                    if station_data is None:
                        raise serializers.ValidationError({
                            'unloading_station': 'Unloading Station data are missing'
                        })

                    unloading_station = Station.unloadingstations.get(
                        pk=station_data.get('id')
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
            due_time: due_time,
            loading_stations:[
                {
                    loading_station: station_id,
                    quality_station: station_id,
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
        assignee_data = self.context.pop('assignee', None)
        if assignee_data is None:
            raise serializers.ValidationError({
                'assignee': 'Assignee data are missing'
            })

        try:
            assignee = m.User.objects.get(id=assignee_data.get('id', None))
        except m.User.DoesNotExist:
            raise serializers.ValidationError({
                'assignee': 'Such user does not exist'
            })

        customer_data = self.context.pop('customer', None)
        if customer_data is None:
            raise serializers.ValidationError({
                'customer': 'Customer data are missing'
            })

        try:
            customer = m.User.objects.get(id=customer_data.get('id', None))
        except m.User.DoesNotExist:
            raise serializers.ValidationError({
                'customer': 'Such customer does not exist'
            })

        loading_stations_data = self.context.pop('loading_stations', None)
        weight_errors = []
        if loading_stations_data is None:
            raise serializers.ValidationError({
                'order': 'Order data are missing'
            })

        for loading_station_data in loading_stations_data:
            products_data = loading_station_data.get(
                'products', None
            )
            if products_data is None:
                raise serializers.ValidationError({
                    'products': 'Order Product data are missing'
                })

            # validate product weights
            product_index = 0
            for product_data in products_data:
                unloading_stations_data = product_data.get(
                    'unloading_stations', None
                )
                if unloading_stations_data is None:
                    raise serializers.ValidationError({
                        'unloading_station':
                        'Unloading stations are not provided'
                    })
                total_weight = float(product_data.get('total_weight', 0))
                total_weight = float(total_weight)
                # TODO: check total weight validation

                for unloading_station_data in unloading_stations_data:
                    # TODO: check unloading station weight validation
                    weight = float(unloading_station_data.get('weight', 0))
                    total_weight = total_weight - weight

                if total_weight != 0:
                    weight_errors.append(product_index)
                product_index = product_index + 1

        if weight_errors:
            raise serializers.ValidationError({
                'weight': weight_errors
            })

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.assignee = assignee
        instance.customer = customer
        instance.save()
        instance.loading_stations.clear()
        # 2. save models
        for loading_station_data in loading_stations_data:
            station_data = loading_station_data.pop('loading_station')
            if station_data is None:
                raise serializers.ValidationError({
                    'loading_station': 'Loading Station data are missing'
                })

            try:
                loading_station = Station.loadingstations.get(
                    id=station_data.get('id', None)
                )
            except Station.DoesNotExist:
                raise serializers.ValidationError({
                    'loading_station': 'Loading Station does not exists'
                })

            station_data = loading_station_data.pop('quality_station')
            if station_data is None:
                raise serializers.ValidationError({
                    'quality_station': 'Quality Station data are missing'
                })
            try:
                quality_station = Station.qualitystations.get(
                    pk=station_data.get('id')
                )
            except Station.DoesNotExist:
                raise serializers.ValidationError({
                    'quality_station': 'Quality Station does not exists'
                })

            products_data = loading_station_data.pop('products')

            order_loading_station = m.OrderLoadingStation.objects.create(
                order=instance,
                loading_station=loading_station,
                quality_station=quality_station,
                **loading_station_data
            )

            for product_data in products_data:
                product = product_data.pop('product', None)
                if product is None:
                    raise serializers.ValidationError({
                        'product': 'Product data are missing'
                    })

                try:
                    product = m.Product.objects.get(
                        id=product.get('id')
                    )
                except m.Product.DoesNotExist:
                    raise serializers.ValidationError({
                        'product': 'Product does not exist'
                    })

                unloading_stations_data = product_data.pop(
                    'unloading_stations'
                )

                product_data['total_weight_measure_unit'] =\
                    product_data['total_weight_measure_unit']['value']
                product_data['price_weight_measure_unit'] =\
                    product_data['price_weight_measure_unit']['value']
                product_data['loss_unit'] =\
                    product_data['loss_unit']['value']
                product_data['payment_method'] =\
                    product_data['payment_method']['value']
                order_product = m.OrderProduct.objects.create(
                    order_loading_station=order_loading_station,
                    product=product,
                    **product_data
                )

                for unloading_station_data in unloading_stations_data:
                    station_data = unloading_station_data.pop('unloading_station')
                    if station_data is None:
                        raise serializers.ValidationError({
                            'unloading_station': 'Unloading Station data are missing'
                        })

                    unloading_station = Station.unloadingstations.get(
                        pk=station_data.get('id')
                    )
                    m.OrderProductDeliver.objects.create(
                        order_product=order_product,
                        unloading_station=unloading_station,
                        **unloading_station_data
                    )
        return instance


class ShortOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Order
        fields = (
            'id', 'alias'
        )


class OrderDataViewSerializer(serializers.ModelSerializer):
    """
    Order serializer
    """
    loading_stations = OrderLoadingStationSerializer(
        source='orderloadingstation_set', many=True, read_only=True
    )

    assignee = ShortUserSerializer(read_only=True)
    customer = ShortUserSerializer(read_only=True)
    order_source = TMSChoiceField(choices=c.ORDER_SOURCE)
    products = ShortProductSerializer(many=True)
    loading_stations_data = ShortStationSerializer(many=True)
    quality_stations_data = ShortStationSerializer(many=True)
    unloading_stations_data = ShortStationSerializer(many=True)
    status = TMSChoiceField(choices=c.ORDER_STATUS)

    class Meta:
        model = m.Order
        fields = '__all__'
