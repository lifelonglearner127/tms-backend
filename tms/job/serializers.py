from django.shortcuts import get_object_or_404

from rest_framework import serializers

from . import models as m
from ..order.models import OrderProductDeliver
from ..vehicle.serializers import ShortVehicleSerializer
from ..account.serializers import ShortStaffProfileSerializer
from ..road.serializers import PathDataSerializer


class MissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Mission
        fields = '__all__'


class JobSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Job
        fields = '__all__'

    def create(self, validated_data):
        mission_ids = self.context.get('missions')
        job = m.Job.objects.create(**validated_data)
        for mission_id in mission_ids:
            mission = get_object_or_404(OrderProductDeliver, pk=mission_id)
            m.Mission.objects.create(
                mission=mission,
                job=job
            )
        return job


class JobDataSerializer(serializers.ModelSerializer):

    vehicle = ShortVehicleSerializer()
    driver = ShortStaffProfileSerializer()
    escort = ShortStaffProfileSerializer()
    path = PathDataSerializer()
    missions = MissionSerializer(
        source='mission_set', many=True, read_only=True
    )

    class Meta:
        model = m.Job
        fields = '__all__'
