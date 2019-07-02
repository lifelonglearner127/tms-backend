from . import models as m
from . import serializers as s

from ..core.views import ApproveViewSet


class ParkingRequestViewSet(ApproveViewSet):

    queryset = m.ParkingRequest.objects.all()
    serializer_class = s.ParkingRequestSerializer
    data_view_serializer = s.ParkingRequestDataViewSerializer


class DriverChangeRequestViewSet(ApproveViewSet):

    queryset = m.DriverChangeRequest.objects.all()
    serializer_class = s.DriverChangeRequestSerializer
    data_view_serializer = s.DriverChangeRequestDataViewSerializer


class EscortChangeRequestViewSet(ApproveViewSet):

    queryset = m.EscortChangeRequest.objects.all()
    serializer_class = s.EscortChangeRequestSerializer
    data_view_serializer = s.EscortChangeRequestDataViewSerializer
