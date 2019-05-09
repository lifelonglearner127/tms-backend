from rest_framework import serializers

from . import models as m


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
