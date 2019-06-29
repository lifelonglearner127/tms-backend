from rest_framework import serializers

from . import models as m
from ..core import constants as c
from ..core.serializers import TMSChoiceField
from ..info.models import Station
from ..info.serializers import ShortStationSerializer, ShortStationPointSerializer


class ShortRouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Route
        fields = (
            'id', 'name'
        )


class RouteSerializer(serializers.ModelSerializer):

    policy = TMSChoiceField(choices=c.ROUTE_PLANNING_POLICY)

    class Meta:
        model = m.Route
        fields = '__all__'


class PathStationNameField(serializers.ListField):

    def to_representation(self, value):
        paths = Station.workstations.filter(id__in=value)
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

        serializer = ShortStationPointSerializer(
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
