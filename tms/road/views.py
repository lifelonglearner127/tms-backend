from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..core.views import TMSViewSet
from . import models as m
from . import serializers as s


class RouteViewSet(TMSViewSet):

    queryset = m.Route.objects.all()
    serializer_class = s.RouteSerializer
    short_serializer_class = s.ShortRouteSerializer
    data_view_serializer_class = s.RouteDataViewSerializer

    @action(detail=True, url_path='points', methods=['get'])
    def get_route_point(self, request, pk=None):
        instance = self.get_object()
        return Response(
            s.RoutePointSerializer(instance).data,
            status=status.HTTP_200_OK
        )
