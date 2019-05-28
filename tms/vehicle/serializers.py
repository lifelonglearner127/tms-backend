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


class VehicleDocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.VehicleDocument
        fields = '__all__'


class VehiclePositionSerializer(serializers.ModelSerializer):
    """
    Serializer for vehicle playback
    """
    lnglat = serializers.SerializerMethodField()

    class Meta:
        model = m.Vehicle
        fields = (
            'plate_num', 'speed', 'lnglat'
        )

    def get_lnglat(self, obj):
        return [obj.longitude, obj.latitude]
