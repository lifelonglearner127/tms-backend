from datetime import datetime

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..g7.interfaces import G7Interface
from ..core.views import StaffViewSet, ChoicesView, ApproveViewSet
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

    def create(self, request):
        branches = request.data.get('branches', None)
        if branches is None:
            load = request.data.get('load', 0)
            data = request.data.copy()
            data.setdefault('branches', [load])
            serializer = self.serializer_class(data=data)
        else:
            serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )

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
        plate_nums = m.Vehicle.objects.values_list('plate_num', flat=True)
        body = {
            'plate_nums': list(plate_nums),
            'fields': ['loc']
        }

        data = G7Interface.call_g7_http_interface(
            'BULK_VEHICLE_STATUS_INQUIRY',
            body=body
        )

        serializer = s.VehiclePositionSerializer(
            list(data.values()), many=True
        )

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


class VehicleMaintenanceRequestViewSet(ApproveViewSet):

    queryset = m.VehicleMaintenanceRequest.objects.all()
    serializer_class = s.VehicleMaintenanceRequestSerializer
    data_view_serializer_class = s.VehicleMaintenanceRequestDataViewSerializer


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
