from rest_framework.decorators import action
from ..core.views import StaffViewSet
from . import models as m
from . import serializers as s


class PointViewSet(StaffViewSet):

    queryset = m.Point.objects.all()
    serializer_class = s.PointSerializer

    @action(detail=False, url_path='black')
    def black_dots(self, request):
        page = self.paginate_queryset(
            m.Point.black.all()
        )

        serializer = self.serializer_class(page, many=True)

        return self.get_paginated_response(serializer.data)


class RouteViewSet(StaffViewSet):

    queryset = m.Route.objects.all()
    serializer_class = s.RouteSerializer
    short_serializer_class = s.ShortRouteSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return s.RouteSerializer
        else:
            return s.RouteDataSerializer
