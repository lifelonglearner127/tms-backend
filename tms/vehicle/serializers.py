from rest_framework import serializers

from .models import Vehicle


class ShortVehicleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vehicle
        fields = (
            'id', 'no'
        )


class VehicleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vehicle
        fields = '__all__'
