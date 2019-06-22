from rest_framework import serializers

from . import models as m
from ..info.models import Station
from ..info.serializers import ShortStationSerializer, StationPointSerializer


class ShortRouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Route
        fields = (
            'id', 'name'
        )


class RouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Route
        fields = '__all__'


class PathStationNameField(serializers.ListField):

    def to_representation(self, value):
        paths = Station.work_stations.filter(id__in=value)
        paths = dict([(point.id, point) for point in paths])

        serializer = ShortStationSerializer(
            [paths[id] for id in value],
            many=True
        )
        return serializer.data


class RouteDataViewSerializer(serializers.ModelSerializer):

    path = PathStationNameField()

    class Meta:
        model = m.Route
        fields = '__all__'


class PathLngLatField(serializers.ListField):

    def to_representation(self, value):
        paths = Station.objects.filter(id__in=value)
        paths = dict([(point.id, point) for point in paths])

        serializer = StationPointSerializer(
            [paths[id] for id in value],
            many=True
        )
        return serializer.data


class RoutePointSerializer(serializers.ModelSerializer):

    path = PathLngLatField()

    class Meta:
        model = m.Route
        fields = (
            'id', 'path'
        )
