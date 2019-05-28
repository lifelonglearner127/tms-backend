from rest_framework import serializers

from . import models as m


class PointSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Point
        fields = (
            'id', 'name', 'address'
        )

    def to_representation(self, point):
        ret = super().to_representation(point)
        ret['lnglat'] = [point.longitude, point.latitude]
        return ret


class BlackPointSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.BlackPoint
        fields = '__all__'


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
        paths = m.Point.objects.filter(id__in=value)
        paths = dict([(point.id, point) for point in paths])

        serializer = PointSerializer(
            [paths[id] for id in value],
            many=True
        )
        return serializer.data


class RouteDataSerializer(serializers.ModelSerializer):

    path = PathField()

    class Meta:
        model = m.Route
        fields = (
            'name', 'policy', 'distance', 'path'
        )
