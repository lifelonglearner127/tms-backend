from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models as m
from . import serializers as s
from ..vehicle.models import Vehicle
from ..core.views import TMSViewSet
from ..core import constants as c


class RouteViewSet(TMSViewSet):

    queryset = m.Route.objects.all()
    serializer_class = s.RouteSerializer
    short_serializer_class = s.ShortRouteSerializer
    page_name = 'routes'

    def create(self, request):
        data = request.data

        context = {
            'start_point': request.data.pop('start_point', None),
            'end_point': request.data.pop('end_point', None),
            'vehicle': request.data.pop('vehicle', None)
        }

        is_g7_route = data.get('is_g7_route', False)
        if not is_g7_route:
            path = []
            for item in data.pop('map_path', []):
                if item.get('id', None):
                    path.append(item.get('id'))
                    continue

                custom_point = m.Station.objects.create(
                    station_type=c.STATION_TYPE_CUSTOM_POINT,
                    latitude=item.pop('latitude'),
                    longitude=item.pop('longitude'),
                    name=item.pop('name')
                )
                path.append(custom_point.id)

            data['map_path'] = path

        serializer = s.RouteSerializer(
            data=data, context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        data = request.data
        context = {
            'start_point': request.data.pop('start_point', None),
            'end_point': request.data.pop('end_point', None),
            'vehicle': request.data.pop('vehicle', None)
        }

        is_g7_route = data.get('is_g7_route', False)
        if not is_g7_route:
            path = []
            for item in data.pop('map_path', []):
                if item.get('id', None):
                    path.append(item.get('id'))
                    continue

                custom_point = m.Station.objects.create(
                    station_type=c.STATION_TYPE_CUSTOM_POINT,
                    latitude=item.pop('latitude'),
                    longitude=item.pop('longitude'),
                    name=item.pop('name')
                )
                path.append(custom_point.id)

            data['map_path'] = path

        serializer = s.RouteSerializer(
            instance, data=data, context=context, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, url_path='points', methods=['get'])
    def get_route_point(self, request, pk=None):
        instance = self.get_object()
        return Response(
            s.RouteSerializer(instance).data,
            status=status.HTTP_200_OK
        )
