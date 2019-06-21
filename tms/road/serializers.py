from rest_framework import serializers

from . import models as m
from ..info.models import Station
from ..info.serializers import ShortStationSerializer


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


class PathField(serializers.ListField):

    def to_representation(self, value):
        paths = Station.work_stations.filter(id__in=value)
        paths = dict([(point.id, point) for point in paths])

        serializer = ShortStationSerializer(
            [paths[id] for id in value],
            many=True
        )
        return serializer.data


class RouteDataSerializer(serializers.ModelSerializer):

    path = PathField()

    class Meta:
        model = m.Route
        fields = '__all__'
