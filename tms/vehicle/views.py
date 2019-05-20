from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from ..openapi.interfaces import G7Interface
from ..core.views import StaffViewSet, ChoicesView
from ..core.constants import VEHICLE_MODEL_TYPE, VEHICLE_BRAND
from . import serializers as s
from . import models as m


class VehicleViewSet(StaffViewSet):
    """
    Viewset for Vehicle
    """
    queryset = m.Vehicle.objects.all()
    serializer_class = s.VehicleSerializer

    @action(detail=False)
    def short(self, request):
        serializer = s.ShortVehicleSerializer(
            m.Vehicle.objects.all(),
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'], url_path='vehicle-playback')
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

                for x in data:
                    paths.append([x.pop('lng'), x.pop('lat')])
                    print(x)
                    x['time'] = datetime.utcfromtimestamp(int(x['time'])/1000).strftime('%Y-%m-%d %H:%M:%S')

                results = {
                    'paths': paths,
                    'meta': data
                }

        return Response(
            results,
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
    static_choices = VEHICLE_MODEL_TYPE


class VehicleBrandAPIView(ChoicesView):
    """
    APIView for returning vehicle brand
    """
    static_choices = VEHICLE_BRAND
