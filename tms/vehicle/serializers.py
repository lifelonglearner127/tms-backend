from rest_framework import serializers

from ..core import constants as c

# models
from . import models as m

# serializers
from ..core.serializers import TMSChoiceField


class FuelConsumptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.FuelConsumption
        fields = '__all__'


class TireSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Tire
        fields = '__all__'


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

    # def validate(self, data):
    #     if data['actual_load'] != sum(data['branches']):
    #         raise serializers.ValidationError({
    #             'branches': 'Sum of branches weight exceed total weight'
    #         })
    #     return data

    def to_internal_value(self, data):
        """
        Exclude date, datetimefield if its string is empty
        """
        for key, value in self.fields.items():
            if isinstance(value, serializers.DateField) and data[key] == '':
                data.pop(key)

        ret = super().to_internal_value(data)
        return ret


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
