from rest_framework import serializers

from . import models as m
from ..hr.serializers import ShortDepartmentSerializer
from ..vehicle.serializers import ShortVehicleSerializer


class OrderPaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.OrderPayment
        fields = '__all__'


class OrderPaymentDataViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.OrderPayment
        fields = '__all__'


class ShortETCCardSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.ETCCard
        fields = (
            'id', 'number'
        )


class ETCCardSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.ETCCard
        fields = '__all__'


class ETCCardDataViewSerializer(serializers.ModelSerializer):

    department = ShortDepartmentSerializer()
    vehicle = ShortVehicleSerializer()

    class Meta:
        model = m.ETCCard
        fields = '__all__'


class ShortFuelCardSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.FuelCard
        fields = (
            'id', 'number'
        )


class FuelCardSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.FuelCard
        fields = '__all__'

    def validate(self, data):
        master = data.get('master', None)
        vehicle = data.get('vehicle', None)
        if master is not None and vehicle is None:
            raise serializers.ValidationError({
                'vehicle': 'Vehicle is required'
            })

        return data


class FuelCardDataViewSerializer(serializers.ModelSerializer):

    department = ShortDepartmentSerializer()
    vehicle = ShortVehicleSerializer()
    master = ShortFuelCardSerializer()

    class Meta:
        model = m.FuelCard
        fields = '__all__'
