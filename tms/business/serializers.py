from rest_framework import serializers

# constants
from ..core import constants as c

# model
from . import models as m
from ..account.models import User

# serializers
from ..core.serializers import TMSChoiceField
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


class RestRequestSerializer(serializers.ModelSerializer):

    user = ShortUserSerializer(read_only=True)
    category = TMSChoiceField(choices=c.REST_REQUEST_CATEGORY)

    class Meta:
        model = m.RestRequest
        fields = '__all__'

    def create(self, validated_data):
        try:
            user_id = self.context.pop('user')
            user = User.companymembers.get(pk=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'user': 'User does not exist'
            })

        return m.RestRequest.objects.create(
            user=user,
            **validated_data
        )

    def update(self, instance, validated_data):
        user_id = self.context.pop('user')
        try:
            user_id = self.context.pop('user')
            user = User.companymembers.get(pk=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'user': 'User does not exist'
            })

        for (key, value) in validated_data.items():
            setattr(instance, key, value)
        instance.user = user
        instance.save()
        return instance

    def validate(self, data):
        from_date = data.get('from_date', None)
        to_date = data.get('to_date', None)

        if from_date > to_date:
            raise serializers.ValidationError({
                'to_date': 'Error'
            })

        return data
