from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models as m
from . import serializers as s
from ..core import constants as c
from ..core.serializers import ChoiceSerializer
from ..core.views import ApproveViewSet, TMSViewSet


class DepartmentViewSet(TMSViewSet):

    queryset = m.Department.objects.all()
    serializer_class = s.DepartmentSerializer
    short_serializer_class = s.ShortDepartmentSerializer


class PositionViewSet(TMSViewSet):

    queryset = m.Position.objects.all()
    serializer_class = s.PositionSerializer
    short_serializer_class = s.ShortPositionSerializer


class RoleManagementViewSet(TMSViewSet):

    queryset = m.RoleManagement.objects.all()
    serializer_class = s.RoleManagementSerializer
    data_view_serializer_class = s.RoleManagementDataViewSerializer


class RestRequestViewSet(ApproveViewSet):

    queryset = m.RestRequest.objects.all()
    serializer_class = s.RestRequestSerializer

    def create(self, request):
        staff_id = request.data.pop('staff', None)

        if staff_id is None:
            staff_id = request.user.profile.id

        context = {
            'staff': staff_id
        }
        print(staff_id)
        serializer = self.serializer_class(
            data=request.data, context=context
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        staff_id = request.data.pop('staff', None)
        if staff_id is None:
            staff_id = request.user.id

        context = {
            'staff': staff_id
        }

        serializer = self.serializer_class(
            instance, data=request.data, context=context, partial=True
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


class StaffProfileViewSet(TMSViewSet):

    queryset = m.StaffProfile.objects.all()
    serializer_class = s.StaffProfileSerializer
    short_serializer_class = s.ShortStaffProfileSerializer
    data_view_serializer_class = s.StaffProfileDataViewSerializer

    def create(self, request):
        context = {
            'user': request.data.pop('user', None),
            'department': request.data.pop('department', None),
            'position': request.data.pop('position', None),
            'driver_license': request.data.pop('driver_license', None)
        }

        serializer = self.serializer_class(
            data=request.data, context=context
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        serializer_instance = self.get_object()
        context = {
            'user': request.data.pop('user', None),
            'department': request.data.pop('department', None),
            'position': request.data.pop('position', None),
            'driver_license': request.data.pop('driver_license', None)
        }

        serializer = self.serializer_class(
            serializer_instance,
            data=request.data,
            context=context,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='short-staff')
    def short_staff(self, request):
        serializer = s.ShortStaffProfileSerializer(
            self.get_queryset().filter(
                user__role__in=[c.USER_ROLE_ADMIN, c.USER_ROLE_STAFF]
            ),
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='short-company-member')
    def short_company_member(self, request):
        serializer = s.ShortStaffProfileSerializer(
            self.get_queryset(),
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class CustomerProfileViewSet(TMSViewSet):

    queryset = m.CustomerProfile.objects.all()
    serializer_class = s.CustomerProfileSerializer
    short_serializer_class = s.ShortCustomerProfileSerializer

    def create(self, request):
        context = {
            'user': request.data.pop('user'),
            'associated_with': request.data.pop('associated_with'),
            'products': request.data.pop('products')
        }

        serializer = self.serializer_class(
            data=request.data, context=context
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        serializer_instance = self.get_object()
        context = {
            'user': request.data.pop('user'),
            'associated_with': request.data.pop('associated_with'),
            'products': request.data.pop('products')
        }

        serializer = self.serializer_class(
            serializer_instance,
            data=request.data,
            context=context,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
