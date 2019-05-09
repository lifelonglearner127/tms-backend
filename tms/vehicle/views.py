from rest_framework import status
from rest_framework.response import Response

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
