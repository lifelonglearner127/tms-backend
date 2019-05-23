from rest_framework import viewsets

from . import models as m
from . import serializers as s


class PointViewSet(viewsets.ModelViewSet):

    queryset = m.Point.objects.all()
    serializer_class = s.PointSerializer


class BlackPointViewSet(viewsets.ModelViewSet):

    queryset = m.BlackPoint.objects.all()
    serializer_class = s.BlackPointSerializer


class PathViewSet(viewsets.ModelViewSet):

    queryset = m.Path.objects.all()
    serializer_class = s.PathSerializer
