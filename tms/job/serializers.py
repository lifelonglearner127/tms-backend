from django.shortcuts import get_object_or_404

from rest_framework import serializers

from . import models as m
from ..core.utils import format_datetime
from ..account.serializers import ShortUserSerializer
from ..order.models import OrderProductDeliver
from ..order.serializers import (
    ShortOrderSerializer, ShortOrderProductDeliverSerializer,
    ShortStationSerializer,
)
from ..info.serializers import ShortProductSerializer
from ..vehicle.serializers import ShortVehicleSerializer
from ..road.serializers import ShortRouteSerializer
from ..finance.serializers import BillDocumentSerializer


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

    driver = ShortUserSerializer()
    escort = ShortUserSerializer()
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


class JobProgressBarField(serializers.Field):

    def to_representation(self, instance):
        ret = []
        if instance.route is not None:
            ret.append({'title': '出发'})
            ret.append({'title': '赶往装货地'})
            ret.append({'title': '到达等待装货'})
            ret.append({'title': '开始装货'})
            ret.append({'title': '录入装货数量'})
            ret.append({'title': '赶往质检地'})
            ret.append({'title': '到达等待质检'})
            ret.append({'title': '开始质检'})
            ret.append({'title': '录入质检量'})

            unloading_stations = instance.route.stations[2:]
            for station in unloading_stations:
                ret.append({'title': '赶往卸货地:' + station.name})
                ret.append({'title': '到达等待卸货:' + station.name})
                ret.append({'title': '开始卸货:' + station.name})
                ret.append({'title': '录入卸货数量:' + station.name})

            ret.append({'title': '完成'})

            progress = 1
            for item in ret:
                item['progress'] = progress
                item['active'] = progress == instance.progress
                progress = progress + 1

        return ret


class StationField(serializers.ListField):

    def to_representation(self, instance):
        if instance.route is not None:
            serializer = ShortStationSerializer(
                instance.route.stations, many=True
            )
            return serializer.data
        else:
            return []


class JobDataViewSerializer(serializers.ModelSerializer):

    vehicle = ShortVehicleSerializer()
    driver = ShortUserSerializer()
    escort = ShortUserSerializer()
    stations = StationField(source='*')
    products = ShortProductSerializer(
        source='order.products', many=True
    )
    progress_bar = JobProgressBarField(source='*')

    class Meta:
        model = m.Job
        fields = (
            'id', 'vehicle', 'driver', 'escort', 'stations', 'products',
            'progress', 'progress_bar', 'total_weight',
            'start_due_time', 'finish_due_time', 'route'
        )


class JobProgressSerializer(serializers.ModelSerializer):

    progress_bar = JobProgressBarField(source='*')

    class Meta:
        model = m.Job
        fields = (
            'id', 'progress_bar'
        )


class JobMileageSerializer(serializers.ModelSerializer):

    order = ShortOrderSerializer()
    vehicle = ShortVehicleSerializer()
    driver = ShortUserSerializer()
    escort = ShortUserSerializer()

    class Meta:
        model = m.Job
        fields = (
            'id', 'order', 'vehicle', 'driver', 'escort', 'total_mileage',
            'empty_mileage', 'heavy_mileage', 'highway_mileage',
            'normalway_mileage'
        )


class LoadingStationTimeField(serializers.Field):

    def to_representation(self, value):
        ret = {
            "arrived_on": format_datetime(value.arrived_loading_station_on),
            "started_working_on": format_datetime(value.started_loading_on),
            "finished_working_on": format_datetime(value.finished_loading_on),
            "departure_on": format_datetime(value.departure_loading_station_on)
        }
        return ret

    def to_internal_value(self, data):
        ret = {
            "arrived_loading_station_on": data['arrived_on']
        }
        return ret


class QualityStationTimeField(serializers.Field):

    def to_representation(self, value):
        ret = {
            "arrived_on": format_datetime(value.arrived_quality_station_on),
            "started_working_on": format_datetime(value.started_checking_on),
            "finished_working_on": format_datetime(value.finished_checking_on),
            "departure_on": format_datetime(value.departure_quality_station_on)
        }
        return ret

    def to_internal_value(self, data):
        ret = {
            "arrived_loading_station_on": data['arrived_on']
        }
        return ret


class UnLoadingStationTimeField(serializers.Field):
    def to_representation(self, value):
        ret = []
        for station in value.all():
            ret.append({
                "arrived_on":
                    format_datetime(station.arrived_station_on),
                "started_working_on":
                    format_datetime(station.started_unloading_on),
                "finished_working_on":
                    format_datetime(station.finished_unloading_on),
                "departure_on":
                    format_datetime(station.departure_station_on)
            })

        return ret

    def to_internal_value(self, data):
        pass


class JobTimeSerializer(serializers.ModelSerializer):

    order = ShortOrderSerializer()
    vehicle = ShortVehicleSerializer()
    driver = ShortUserSerializer()
    escort = ShortUserSerializer()
    loading_station_time = LoadingStationTimeField(source='*')
    quality_station_time = QualityStationTimeField(source='*')
    unloading_station_time = UnLoadingStationTimeField(source='mission_set')

    class Meta:
        model = m.Job
        fields = (
            'id', 'order', 'vehicle', 'driver', 'escort', 'started_on',
            'finished_on', 'loading_station_time', 'quality_station_time',
            'unloading_station_time'
        )


class JobCostSerializer(serializers.ModelSerializer):

    order = ShortOrderSerializer()
    vehicle = ShortVehicleSerializer()
    bills = BillDocumentSerializer(many=True)

    class Meta:
        model = m.Job
        fields = (
            'id', 'order', 'vehicle', 'bills'
        )


class ParkingRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.ParkingRequest
        fields = '__all__'


class ParkingRequestDataViewSerializer(serializers.ModelSerializer):

    vehicle = ShortVehicleSerializer()
    driver = ShortUserSerializer()
    escort = ShortUserSerializer()

    class Meta:
        model = m.ParkingRequest
        fields = '__all__'


class DriverChangeRequestSerializer(serializers.ModelSerializer):
    """
    TODO:
        1) Validation - new driver should be different from job's driver
    """
    class Meta:
        model = m.DriverChangeRequest
        fields = '__all__'


class DriverChangeRequestDataViewSerializer(serializers.ModelSerializer):

    job = ShortJobSerializer()
    new_driver = ShortUserSerializer()

    class Meta:
        model = m.DriverChangeRequest
        fields = '__all__'


class EscortChangeRequestSerializer(serializers.ModelSerializer):
    """
    TODO:
        1) Validation - new escort should be different from job's escort
    """
    class Meta:
        model = m.EscortChangeRequest
        fields = '__all__'


class EscortChangeRequestDataViewSerializer(serializers.ModelSerializer):

    job = ShortJobSerializer()
    new_escort = ShortUserSerializer()

    class Meta:
        model = m.EscortChangeRequest
        fields = '__all__'
