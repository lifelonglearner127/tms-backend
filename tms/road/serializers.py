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
