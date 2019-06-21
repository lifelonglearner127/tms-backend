from rest_framework.decorators import action
from ..core.views import StaffViewSet
from . import models as m
from . import serializers as s


class RouteViewSet(StaffViewSet):

    queryset = m.Route.objects.all()
    serializer_class = s.RouteSerializer
    short_serializer_class = s.ShortRouteSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return s.RouteSerializer
        else:
            return s.RouteDataSerializer
