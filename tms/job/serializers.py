from django.shortcuts import get_object_or_404

from rest_framework import serializers

from . import models as m
from ..order.models import OrderProductDeliver


class MissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Mission
        fields = '__all__'


class JobSerializer(serializers.ModelSerializer):

    unloading_stations = MissionSerializer(
        source='mission_set', many=True, read_only=True
    )

    class Meta:
        model = m.Job
        fields = '__all__'

    def create(self, validated_data):
        mission_id = self.context.get('mission')
        mission = get_object_or_404(OrderProductDeliver, pk=mission_id)
        job = m.Job.objects.create(**validated_data)
        m.Mission.objects.create(
            mission=mission,
            job=job
        )
        return job
