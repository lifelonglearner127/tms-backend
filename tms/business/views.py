from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

# constants
from ..core import constants as c

# models
from . import models as m

# serializers
from . import serializers as s
from ..core.serializers import ChoiceSerializer

# views
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


class RestRequestViewSet(ApproveViewSet):

    queryset = m.RestRequest.objects.all()
    serializer_class = s.RestRequestSerializer

    def create(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={
                'user': request.user
            }
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        serializer = self.serializer_class(
            instance, data=request.data,
            context={
                'user': request.user
            },
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="categories")
    def get_rest_request_cateogires(self, request):
        serializer = ChoiceSerializer(
            [
                {'value': x, 'text': y} for (x, y) in c.REST_REQUEST_CATEGORY
            ],
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
