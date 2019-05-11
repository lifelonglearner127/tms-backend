from rest_framework import serializers

from . import models as m
from ..info.models import Product, UnLoadingStation, LoadingStation
from ..info.serializers import (
    ShortUnLoadingStationSerializer, ShortLoadingStationSerializer,
    ShortProductSerializer
)
from ..account.serializers import (
    ShortCustomerProfileSerializer, ShortStaffProfileSerializer
)
from ..account.models import StaffProfile, CustomerProfile
from ..vehicle.models import Vehicle
from ..vehicle.serializers import ShortVehicleSerializer


class JobSerializer(serializers.ModelSerializer):

    vehicle = ShortVehicleSerializer(read_only=True)
    driver = ShortStaffProfileSerializer(read_only=True)
    escort = ShortStaffProfileSerializer(read_only=True)

    class Meta:
        model = m.Job
        fields = (
            'id', 'vehicle', 'driver', 'escort'
        )


class OrderProductDeliverSerializer(serializers.ModelSerializer):
    """
    Serializer for unloading stations selected for product delivery
    """
    unloading_station = ShortUnLoadingStationSerializer(
        read_only=True
    )

    jobs = JobSerializer(
        source='job_set', many=True, read_only=True
    )

    class Meta:
        model = m.OrderProductDeliver
        fields = (
            'id', 'weight', 'unloading_station', 'jobs'
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


class OrderSerializer(serializers.ModelSerializer):
    """
    Order serializer
    """
    products = OrderProductSerializer(
        source='orderproduct_set', many=True, read_only=True
    )

    loading_station = ShortLoadingStationSerializer(read_only=True)
    assignee = ShortStaffProfileSerializer(read_only=True)
    customer = ShortCustomerProfileSerializer(read_only=True)

    class Meta:
        model = m.Order
        fields = '__all__'

    def create(self, validated_data):
        # get customer
        customer_data = self.context.get('customer', None)
        if customer_data is None:
            raise serializers.ValidationError('Customer data is not provided')

        customer_id = customer_data.get('id', None)
        try:
            customer = CustomerProfile.objects.get(pk=customer_id)
        except CustomerProfile.DoesNotExist:
            raise serializers.ValidationError('Such customer does not exist')

        # get assignee
        assignee_data = self.context.get('assignee', None)
        if assignee_data is None:
            raise serializers.ValidationError('Assignee data is not provided')

        assignee_id = assignee_data.get('id', None)
        try:
            assignee = StaffProfile.objects.get(pk=assignee_id)
        except StaffProfile.DoesNotExist:
            raise serializers.ValidationError('Such staff does not exist')

        # get loading station
        loading_station_data = self.context.get('loading_station', None)
        if loading_station_data is None:
            raise serializers.ValidationError('Assignee data is not provided')

        loading_station_id = loading_station_data.get('id', None)
        try:
            loading_station = LoadingStation.objects.get(
                pk=loading_station_id
            )
        except LoadingStation.DoesNotExist:
            raise serializers.ValidationError(
                'Such loading station does not exist'
            )

        order = m.Order.objects.create(
            loading_station=loading_station,
            assignee=assignee,
            customer=customer,
            **validated_data
        )

        # get ordred products
        ordered_products_delivers = self.context.get('products', None)
        if ordered_products_delivers is None:
            raise serializers.ValidationError('Product is not provided')

        for product_deliver in ordered_products_delivers:
            # get ordered details of each products
            product_data = product_deliver.pop('product', None)
            unloading_stations_delivers = product_deliver.pop(
                'unloading_stations', None
            )

            if product_data is None:
                raise serializers.ValidationError(
                    'Ordered Product is not provided'
                    )

            product_id = product_data.get('id', None)
            try:
                product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                raise serializers.ValidationError(
                    'Such product does not exist'
                    )

            order_product = m.OrderProduct.objects.create(
                order=order, product=product, **product_deliver
            )

            # get unloading stations of each ordered products
            if unloading_stations_delivers is None:
                raise serializers.ValidationError(
                    'Unloading station is not provided'
                    )

            for unloading_station_deliver in unloading_stations_delivers:
                # get unlaoding station
                unloading_station_data = unloading_station_deliver.pop(
                    'unloading_station', None
                    )
                if unloading_station_data is None:
                    raise serializers.ValidationError(
                        'Unloading station is not provided'
                        )

                unloading_station_id = unloading_station_data.get('id', None)
                try:
                    unloading_station = UnLoadingStation.objects.get(
                        pk=unloading_station_id
                    )
                except UnLoadingStation.DoesNotExist:
                    raise serializers.ValidationError(
                        'Such unloading station does not exist'
                        )

                m.OrderProductDeliver.objects.create(
                    order_product=order_product,
                    unloading_station=unloading_station,
                    **unloading_station_deliver
                )

        return order

    def update(self, instance, validated_data):
        # get customer
        customer_data = self.context.get('customer', None)
        if customer_data is None:
            raise serializers.ValidationError('Customer data is not provided')

        customer_id = customer_data.get('id', None)
        try:
            customer = CustomerProfile.objects.get(pk=customer_id)
        except CustomerProfile.DoesNotExist:
            raise serializers.ValidationError('Such customer does not exist')

        # get assignee
        assignee_data = self.context.get('assignee', None)
        if assignee_data is None:
            raise serializers.ValidationError('Assignee data is not provided')

        assignee_id = assignee_data.get('id', None)
        try:
            assignee = StaffProfile.objects.get(pk=assignee_id)
        except StaffProfile.DoesNotExist:
            raise serializers.ValidationError('Such staff does not exist')

        # get loading station
        loading_station_data = self.context.get('loading_station', None)
        if loading_station_data is None:
            raise serializers.ValidationError('Assignee data is not provided')

        loading_station_id = loading_station_data.get('id', None)
        try:
            loading_station = LoadingStation.objects.get(
                pk=loading_station_id
            )
        except LoadingStation.DoesNotExist:
            raise serializers.ValidationError(
                'Such loading station does not exist'
                )

        instance.loading_station = loading_station
        instance.assignee = assignee
        instance.customer = customer

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        instance.products.clear()

        # get ordred products
        ordered_products_delivers = self.context.get('products', None)
        if ordered_products_delivers is None:
            raise serializers.ValidationError('Product is not provided')

        for product_deliver in ordered_products_delivers:
            # get ordered details of each products
            product_data = product_deliver.pop('product', None)
            unloading_stations_delivers = product_deliver.pop(
                'unloading_stations', None
            )
            if product_data is None:
                raise serializers.ValidationError(
                    'Ordered Product is not provided'
                    )

            product_id = product_data.get('id', None)
            try:
                product = m.Product.objects.get(pk=product_id)
            except m.Product.DoesNotExist:
                raise serializers.ValidationError(
                    'Such product does not exist'
                    )

            order_product = m.OrderProduct.objects.create(
                order=instance, product=product, **product_deliver
            )

            # get unloading stations of each ordered products
            if unloading_stations_delivers is None:
                raise serializers.ValidationError(
                    'Unloading station is not provided'
                )

            for unloading_station_deliver in unloading_stations_delivers:
                jobs = unloading_station_deliver.pop('jobs', None)
                # get unlaoding station
                unloading_station_data = unloading_station_deliver.pop(
                    'unloading_station', None
                    )
                if unloading_station_data is None:
                    raise serializers.ValidationError(
                        'Unloading station is not provided'
                    )

                unloading_station_id = unloading_station_data.get('id', None)
                try:
                    unloading_station = UnLoadingStation.objects.get(
                        pk=unloading_station_id
                    )
                except UnLoadingStation.DoesNotExist:
                    raise serializers.ValidationError(
                        'Such unloading station does not exist'
                    )

                deliver = m.OrderProductDeliver.objects.create(
                    order_product=order_product,
                    unloading_station=unloading_station,
                    **unloading_station_deliver
                )

                for job in jobs:
                    driver_data = job.get('driver', None)
                    if driver_data is None:
                        raise serializers.ValidationError(
                            'driver is not provided'
                        )
                    try:
                        driver_id = driver_data.get('id', None)
                        driver = StaffProfile.drivers.get(pk=driver_id)
                    except StaffProfile.DoesNotExist:
                        raise serializers.ValidationError(
                            'Such driver does not exist'
                        )

                    esocrt_data = job.get('escort', None)
                    if esocrt_data is None:
                        raise serializers.ValidationError(
                            'driver is not provided'
                        )
                    try:
                        escort_id = esocrt_data.get('id', None)
                        escort = StaffProfile.escorts.get(pk=escort_id)
                    except StaffProfile.DoesNotExist:
                        raise serializers.ValidationError(
                            'Such escort does not exist'
                        )

                    vehicle_data = job.get('vehicle', None)
                    if vehicle_data is None:
                        raise serializers.ValidationError(
                            'vehhicle is not provided'
                        )
                    try:
                        vehicle_id = vehicle_data.get('id', None)
                        vehicle = Vehicle.objects.get(pk=vehicle_id)
                    except StaffProfile.DoesNotExist:
                        raise serializers.ValidationError(
                            'Such driver does not exist'
                        )

                    m.Job.objects.create(
                        mission=deliver,
                        vehicle=vehicle,
                        driver=driver,
                        escort=escort
                    )

        return instance
