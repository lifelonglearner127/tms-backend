from rest_framework import serializers

from . import models as m


class PointSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Point
        fields = '__all__'


class BlackPointSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.BlackPoint
        fields = '__all__'


class PathSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Path
        fields = '__all__'


class WayPointsField(serializers.ListField):

    def to_representation(self, value):

        serializer = PointSerializer(
            m.Point.objects.filter(pk__in=value),
            many=True
        )
        return serializer.data


class PathListSerializer(serializers.ModelSerializer):

    origin = PointSerializer()
    destination = PointSerializer()
    way_points = WayPointsField()

    class Meta:
        model = m.Path
        fields = '__all__'
