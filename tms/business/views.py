from django.db.models import Q
from django.utils import timezone as datetime
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..core import constants as c
from ..core.views import ApproveViewSet, TMSViewSet

from . import models as m
from . import serializers as s
from ..finance.serializers import BillDocumentSerializer


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
