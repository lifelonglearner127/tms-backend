from rest_framework import viewsets

from ..core.permissions import IsAccountStaffOrReadOnly
from .models import Vehicle
from .serializers import VehicleSerializer


class VehicleViewSet(viewsets.ModelViewSet):

    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAccountStaffOrReadOnly]
