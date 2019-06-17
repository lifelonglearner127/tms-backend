from rest_framework import serializers

from . import models as m


class ShortVehicleSerializer(serializers.ModelSerializer):
    """
    Serializer for short data of vehicle
    """
    class Meta:
        model = m.Vehicle
        fields = (
            'id', 'plate_num'
        )


class MainVehicleSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Vehicle
        fields = (
            'id', 'plate_num', 'longitude', 'latitude', 'speed'
        )


class VehicleSerializer(serializers.ModelSerializer):
    """
    Vehicle serializer
    """
    class Meta:
        model = m.Vehicle
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['model_display'] = instance.get_model_display()
        ret['brand_display'] = instance.get_brand_display()
        return ret

    def validate(self, data):
        if data['load'] != sum(data['branches']):
            raise serializers.ValidationError({
                'branches': 'Sum of branches weight exceed total weight'
            })
        return data


class VehiclePositionSerializer(serializers.ModelSerializer):
    """
    Serializer for vehicle playback
    """
    lnglat = serializers.SerializerMethodField()

    class Meta:
        model = m.Vehicle
        fields = (
            'id', 'lnglat'
        )

    def get_lnglat(self, obj):
        return [obj.longitude, obj.latitude]


class VehicleMaintenanceRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.VehicleMaintenanceRequest
        fields = '__all__'


class VehicleMaintenanceRequestDataViewSerializer(serializers.ModelSerializer):

    vehicle = ShortVehicleSerializer()

    class Meta:
        model = m.VehicleMaintenanceRequest
        fields = '__all__'
