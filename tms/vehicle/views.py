from ..core.views import StaffViewSet, ChoicesView
from ..core.constants import VEHICLE_MODEL_TYPE, VEHICLE_BRAND
from .models import Vehicle
from .serializers import VehicleSerializer


class VehicleModelAPIView(ChoicesView):

    static_choices = VEHICLE_MODEL_TYPE


class VehicleBrandAPIView(ChoicesView):

    static_choices = VEHICLE_BRAND


class VehicleViewSet(StaffViewSet):

    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
