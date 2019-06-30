from rest_framework import serializers

# model
from . import models as m

# serializers
from ..account.serializers import ShortUserSerializer
from ..vehicle.serializers import ShortVehicleSerializer
from ..order.serializers import ShortJobSerializer


class ParkingRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.ParkingRequest
        fields = '__all__'


class ParkingRequestDataViewSerializer(serializers.ModelSerializer):

    vehicle = ShortVehicleSerializer()
    driver = ShortUserSerializer()
    escort = ShortUserSerializer()

    class Meta:
        model = m.ParkingRequest
        fields = '__all__'


class DriverChangeRequestSerializer(serializers.ModelSerializer):
    """
    TODO:
        1) Validation - new driver should be different from job's driver
    """
    class Meta:
        model = m.DriverChangeRequest
        fields = '__all__'


class DriverChangeRequestDataViewSerializer(serializers.ModelSerializer):

    job = ShortJobSerializer()
    new_driver = ShortUserSerializer()

    class Meta:
        model = m.DriverChangeRequest
        fields = '__all__'


class EscortChangeRequestSerializer(serializers.ModelSerializer):
    """
    TODO:
        1) Validation - new escort should be different from job's escort
    """
    class Meta:
        model = m.EscortChangeRequest
        fields = '__all__'


class EscortChangeRequestDataViewSerializer(serializers.ModelSerializer):

    job = ShortJobSerializer()
    new_escort = ShortUserSerializer()

    class Meta:
        model = m.EscortChangeRequest
        fields = '__all__'
