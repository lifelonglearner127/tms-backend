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


class VehiclePlaybackSerializer(serializers.Serializer):
    """
    Serializer for vehicle playback
    """
    lat = serializers.FloatField()
    lng = serializers.FloatField()
    speed = serializers.IntegerField()
    course = serializers.IntegerField()
    time = serializers.IntegerField()
