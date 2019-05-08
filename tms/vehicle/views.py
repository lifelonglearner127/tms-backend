from ..core.views import StaffViewSet, ChoicesView
from ..core.constants import VEHICLE_MODEL_TYPE, VEHICLE_BRAND
from . import serializers as s
from . import models as m


class VehicleViewSet(StaffViewSet):
    """
    APIView for returning backend contant choices
    """
    queryset = m.Vehicle.objects.all()
    serializer_class = s.VehicleSerializer


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
