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


class VehiclePositionSerializer(serializers.Serializer):
    """
    Serializer for vehicle playback
    """
    plate_num = serializers.CharField()
    lnglat = serializers.SerializerMethodField()

    def get_lnglat(self, obj):
        return [float(obj['data']['loc']['lng']), float(obj['data']['loc']['lat'])]


class VehicleMaintenanceRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.VehicleMaintenanceRequest
        fields = '__all__'


class VehicleMaintenanceRequestDataViewSerializer(serializers.ModelSerializer):

    vehicle = ShortVehicleSerializer()

    class Meta:
        model = m.VehicleMaintenanceRequest
        fields = '__all__'
