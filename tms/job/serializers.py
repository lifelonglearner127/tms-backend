from django.shortcuts import get_object_or_404

from rest_framework import serializers

from . import models as m
from ..order.models import OrderProductDeliver
from ..order.serializers import (
    ShortOrderProductDeliverSerializer, ShortStationSerializer,
)
from ..vehicle.serializers import ShortVehicleSerializer
from ..account.serializers import ShortStaffProfileSerializer
from ..road.serializers import RouteDataSerializer, ShortRouteSerializer


class ShortMissionSerializer(serializers.ModelSerializer):

    mission = ShortOrderProductDeliverSerializer()

    class Meta:
        model = m.Mission
        fields = (
            'mission', 'mission_weight'
        )


class MissionSerializer(serializers.ModelSerializer):

    mission = ShortOrderProductDeliverSerializer()

    class Meta:
        model = m.Mission
        fields = (
            'mission_weight', 'loading_weight', 'unloading_weight',
            'arrived_station_on', 'started_unloading_on',
            'finished_unloading_on', 'departure_station_on',
            'is_completed', 'mission'
        )


class ShortJobSerializer(serializers.ModelSerializer):

    driver = ShortStaffProfileSerializer()
    escort = ShortStaffProfileSerializer()
    vehicle = ShortVehicleSerializer()
    route = ShortRouteSerializer()
    missions = ShortMissionSerializer(
        source='mission_set', many=True, read_only=True
    )

    class Meta:
        model = m.Job
        fields = (
            'driver', 'escort', 'vehicle', 'missions', 'route'
        )


class JobSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Job
        fields = '__all__'

    def create(self, validated_data):
        mission_ids = self.context.get('mission_ids')
        mission_weights = self.context.get('mission_weights')
        job = m.Job.objects.create(**validated_data)
        stations = job.route.stations[2:]

        for i, mission_id in enumerate(mission_ids):
            mission = get_object_or_404(OrderProductDeliver, pk=mission_id)
            m.Mission.objects.create(
                mission=mission,
                job=job,
                step=stations.index(mission.unloading_station),
                mission_weight=mission_weights[i]
            )
        return job


class JobDataSerializer(serializers.ModelSerializer):

    vehicle = ShortVehicleSerializer()
    driver = ShortStaffProfileSerializer()
    escort = ShortStaffProfileSerializer()
    route = RouteDataSerializer()
    missions = ShortMissionSerializer(
        source='mission_set', many=True, read_only=True
    )
    loading_station = ShortStationSerializer(
        source='route.loading_station', read_only=True
    )
    quality_station = ShortStationSerializer(
        source='route.quality_station', read_only=True
    )
    progress_msg = serializers.CharField(source='get_progress_display')
    mission_count = serializers.SerializerMethodField()

    class Meta:
        model = m.Job
        fields = (
            'id', 'vehicle', 'driver', 'escort', 'loading_station',
            'quality_station', 'route', 'missions', 'progress',
            'progress_msg', 'total_weight', 'start_due_time',
            'finish_due_time', 'mission_count', 'is_paid'
        )

    def get_mission_count(self, obj):
        return obj.missions.all().count()


class JobProgressSerializer(serializers.ModelSerializer):

    progress_msg = serializers.CharField(source='get_progress_display')

    class Meta:
        model = m.Job
        fields = (
            'id', 'progress', 'progress_msg'
        )


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid

        if isinstance(data, six.string_types) and\
           data.startswith('data:image'):

            header, data = data.split(';base64,')

            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            file_name = str(uuid.uuid4())[:12]
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = "%s.%s" % (file_name, file_extension, )
            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class JobBillDocumentSerializer(serializers.ModelSerializer):

    document = Base64ImageField()

    class Meta:
        model = m.JobBillDocument
        fields = '__all__'


class DriverNotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.DriverNotification
        fields = (
            'message', 'sent', 'is_read'
        )
