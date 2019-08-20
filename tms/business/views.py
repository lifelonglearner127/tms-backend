from django.shortcuts import get_object_or_404
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
from ..core.views import TMSViewSet


class ParkingRequestViewSet(TMSViewSet):

    queryset = m.ParkingRequest.objects.all()
    serializer_class = s.ParkingRequestSerializer
    data_view_serializer = s.ParkingRequestDataViewSerializer

    def create(self, request):
        data = request.data
        data['driver'] = request.user.id
        serializer = self.serializer_class(
            data=data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        data = request.data
        data['driver'] = request.user.id
        serializer = self.serializer_class(
            instance, data=data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class DriverChangeRequestViewSet(TMSViewSet):

    queryset = m.DriverChangeRequest.objects.all()
    serializer_class = s.DriverChangeRequestSerializer

    def create(self, request):
        data = request.data
        data['old_driver'] = request.user.id
        serializer = self.serializer_class(
            data=data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        data = request.data
        data['old_driver'] = request.user.id
        if data['new_driver'] == data['old_driver']:
            raise s.serializers.ValidationError({
                'new_driver': 'Cannot set the same driver'
            })

        serializer = self.serializer_class(
            instance, data=data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class EscortChangeRequestViewSet(TMSViewSet):

    queryset = m.EscortChangeRequest.objects.all()
    serializer_class = s.EscortChangeRequestSerializer
    data_view_serializer = s.EscortChangeRequestDataViewSerializer

    def create(self, request):
        data = request.data
        data['old_escort'] = request.user.id
        serializer = self.serializer_class(
            data=data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        data = request.data
        data['old_escort'] = request.user.id
        if data['new_escort'] == data['old_escort']:
            raise s.serializers.ValidationError({
                'new_escort': 'Cannot set the same escort'
            })

        serializer = self.serializer_class(
            instance, data=data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class RestRequestViewSet(TMSViewSet):

    queryset = m.RestRequest.objects.all()
    serializer_class = s.RestRequestSerializer

    def create(self, request):
        approvers = request.data.pop('approvers', [])
        ccs = request.data.pop('ccs', [])
        serializer = self.serializer_class(
            data=request.data,
            context={
                'user': request.user, 'approvers': approvers, 'ccs': ccs
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
        approvers = request.data.pop('approvers', [])
        ccs = request.data.pop('ccs', [])
        serializer = self.serializer_class(
            instance, data=request.data,
            context={
                'user': request.user, 'approvers': approvers, 'ccs': ccs
            },
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], url_path="approve")
    def approve(self, request, pk=None):
        rest_request = self.get_object()
        approver = request.user
        if approver not in rest_request.approvers.all():
            return Response(
                {'request': 'You cannot handle this request'},
                status=status.HTTP_403_FORBIDDEN
            )

        rest_request_approve = m.RestRequestApprover.objects.filter(
            rest_request=rest_request, approver=approver
        ).first()

        rest_request_approve.approved = request.data.get('approved', False)
        rest_request_approve.description = request.data.get('description', '')
        rest_request_approve.save()

        if not m.RestRequestApprover.objects.filter(rest_request=rest_request, approved=False).exists():
            rest_request.approved = True
            rest_request.save()

        return Response(
            s.RestRequestApproverSerializer(rest_request_approve).data,
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


class VehicleRepairRequestViewSet(TMSViewSet):

    queryset = m.VehicleRepairRequest.objects.all()
    serializer_class = s.VehicleRepairRequestSerializer

    def create(self, request):
        # approvers = request.data.pop('approvers', [])
        # ccs = request.data.pop('ccs', [])
        vehicle_data = request.data.pop('vehicle')
        vehicle = get_object_or_404(m.Vehicle, id=vehicle_data.get('id', None))
        requester = request.data.pop('requester')
        if requester is not None:
            requester = get_object_or_404(m.User, id=requester.get('id', None))
        else:
            requester = request.user

        serializer = self.serializer_class(
            data=request.data,
            context={
                'requester': requester, 'vehicle': vehicle
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
        # approvers = request.data.pop('approvers', [])
        # ccs = request.data.pop('ccs', [])
        vehicle_data = request.data.pop('vehicle')
        vehicle = get_object_or_404(m.Vehicle, id=vehicle_data.get('id', None))
        requester = request.data.pop('requester')
        if requester is not None:
            requester = get_object_or_404(m.User, id=requester.get('id', None))
        else:
            requester = request.user

        serializer = self.serializer_class(
            instance, data=request.data,
            context={
                'requester': requester, 'vehicle': vehicle
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
                {'value': x, 'text': y} for (x, y) in c.VEHICLE_REPAIR_REQUEST_CATEGORY
            ],
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
