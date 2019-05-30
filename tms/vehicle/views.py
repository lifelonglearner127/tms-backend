from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from ..g7.interfaces import G7Interface
from ..core.views import StaffViewSet, ChoicesView
from ..core import constants as c
from . import serializers as s
from . import models as m


class VehicleViewSet(StaffViewSet):
    """
    Viewset for Vehicle
    """
    queryset = m.Vehicle.objects.all()
    serializer_class = s.VehicleSerializer
    short_serializer_class = s.ShortVehicleSerializer

    @action(detail=True, methods=['get'], url_path='playback')
    def vehicle_history_track_query(self, request, pk=None):
        vehicle = self.get_object()
        from_datetime = self.request.query_params.get('from', None)
        to_datetime = self.request.query_params.get('to', None)

        if from_datetime is None or to_datetime is None:
            results = []
        else:
            queries = {
                'plate_num': vehicle.plate_num,
                'from': from_datetime,
                'to': to_datetime,
                'timeInterval': 10
            }

            data = G7Interface.call_g7_http_interface(
                'VEHICLE_HISTORY_TRACK_QUERY',
                queries=queries
            )

            if data is None:
                results = []
            else:
                paths = []

                index = 0
                for x in data:
                    paths.append([x.pop('lng'), x.pop('lat')])
                    print(x)
                    x['no'] = index
                    x['time'] = datetime.utcfromtimestamp(
                        int(x['time'])/1000
                    ).strftime('%Y-%m-%d %H:%M:%S')
                    index = index + 1

                results = {
                    'paths': paths,
                    'meta': data
                }

        return Response(
            results,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='position')
    def vehicle_position(self, request):
        vehicles = m.Vehicle.objects.exclude(
            longitude__isnull=True
        ).exclude(
            latitude__isnull=True
        )
        serializer = s.VehiclePositionSerializer(vehicles, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, url_path="current_info")
    def current_info(self, request, pk=None):
        vehicle = self.get_object()
        # todo: get bound of vehicle with driver and escort

        queries = {
            'plate_num': vehicle.plate_num,
            'fields': 'loc, status',
            'addr_required': True,
        }

        data = G7Interface.call_g7_http_interface(
            'VEHICLE_STATUS_INQUIRY',
            queries=queries
        )

        ret = {
            'plate_num': vehicle.plate_num,
            'driver': 'Driver',
            'escort': 'Escort',
            'gpsno': data['gpsno'],
            'location': data['loc']['address'],
            'speed': data['loc']['speed']
        }
        return Response(
            ret,
            status=status.HTTP_200_OK
        )


class VehicleDocumentViewSet(StaffViewSet):
    """
    Viewset for Vehicle Document
    """
    serializer_class = s.VehicleDocumentSerializer

    def get_queryset(self):
        return m.VehicleDocument.objects.filter(
            vehicle__id=self.kwargs['vehicle_pk']
        )

    def create(self, request, vehicle_pk=None):
        data = request.data.copy()
        data.setdefault('vehicle', vehicle_pk)

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )

    def update(self, request, vehicle_pk=None, pk=None):
        data = request.data.copy()
        data.setdefault('vehicle', vehicle_pk)

        instance = self.get_object()
        serializer = self.serializer_class(
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data, status=status.HTTP_200_OK
        )


class VehicleModelAPIView(ChoicesView):
    """
    APIView for returning vehicle models
    """
    static_choices = c.VEHICLE_MODEL_TYPE


class VehicleBrandAPIView(ChoicesView):
    """
    APIView for returning vehicle brand
    """
    static_choices = c.VEHICLE_BRAND
