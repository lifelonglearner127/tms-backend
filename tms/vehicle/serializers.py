from rest_framework import serializers

from . import models as m
from ..core import constants as c
from ..core.serializers import TMSChoiceField


class ShortVehicleSerializer(serializers.ModelSerializer):
    """
    Serializer for short data of vehicle
    """
    class Meta:
        model = m.Vehicle
        fields = (
            'id', 'plate_num'
        )


class VehicleSerializer(serializers.ModelSerializer):
    """
    Vehicle serializer
    """
    model = TMSChoiceField(choices=c.VEHICLE_MODEL_TYPE)
    brand = TMSChoiceField(choices=c.VEHICLE_BRAND)

    class Meta:
        model = m.Vehicle
        fields = '__all__'

    def validate(self, data):
        if data['load'] != sum(data['branches']):
            raise serializers.ValidationError({
                'branches': 'Sum of branches weight exceed total weight'
            })
        return data


class VehiclePositionSerializer(serializers.Serializer):
    """
    Serializer for vehicle playback
    """
    plate_num = serializers.CharField()
    lnglat = serializers.SerializerMethodField()
    speed = serializers.SerializerMethodField()

    def get_lnglat(self, obj):
        return [
            float(obj['data']['loc']['lng']), float(obj['data']['loc']['lat'])
        ]

    def get_speed(self, obj):
        return [int(obj['data']['loc']['speed'])]


class VehicleMaintenanceRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.VehicleMaintenanceRequest
        fields = '__all__'

    def validate(self, data):
        maintenance_from = data.get('maintenance_from', None)
        maintenance_to = data.get('maintenance_to', None)

        if maintenance_from > maintenance_to:
            raise serializers.ValidationError({
                'maintenance_to': 'Error'
            })

        return data


class VehicleMaintenanceRequestDataViewSerializer(serializers.ModelSerializer):

    vehicle = ShortVehicleSerializer()

    class Meta:
        model = m.VehicleMaintenanceRequest
        fields = '__all__'
