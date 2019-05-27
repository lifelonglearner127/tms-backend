from rest_framework import serializers

from . import models as m


class ShortVehicleSerializer(serializers.ModelSerializer):
    """
    Serializer for short data of vehicle
    """
    class Meta:
        model = m.Vehicle
        fields = '__all__'


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
    position = serializers.SerializerMethodField()

    class Meta:
        model = m.Vehicle
        fields = (
            'plate_num', 'speed', 'position'
        )

    def get_position(self, obj):
        return [obj.longitude, obj.latitude]
