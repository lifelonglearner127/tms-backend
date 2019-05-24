from rest_framework import viewsets

from ..core.views import StaffViewSet
from . import models as m
from . import serializers as s


class PointViewSet(StaffViewSet):

    queryset = m.Point.objects.all()
    serializer_class = s.PointSerializer


class BlackPointViewSet(viewsets.ModelViewSet):

    queryset = m.BlackPoint.objects.all()
    serializer_class = s.BlackPointSerializer


class RouteViewSet(viewsets.ModelViewSet):

    queryset = m.Route.objects.all()
    serializer_class = s.RouteSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return s.RouteSerializer
        else:
            return s.RouteDataSerializer
