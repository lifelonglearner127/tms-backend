from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models as m
from . import serializers as s
from ..core import constants as c
from ..core.permissions import IsDriverOrEscortUser
from ..core.views import TMSViewSet


class DepartmentViewSet(TMSViewSet):

    queryset = m.Department.objects.all()
    serializer_class = s.DepartmentSerializer
    short_serializer_class = s.ShortDepartmentSerializer

    @action(detail=False, url_path='list-departments')
    def get_short_departments(self, request):
        page = self.paginate_queryset(self.queryset)
        serializer = s.ShortDepartmentSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class PositionViewSet(TMSViewSet):

    queryset = m.Position.objects.all()
    serializer_class = s.PositionSerializer
    short_serializer_class = s.ShortPositionSerializer


class RoleManagementViewSet(TMSViewSet):

    queryset = m.RoleManagement.objects.all()
    serializer_class = s.RoleManagementSerializer


class StaffProfileViewSet(TMSViewSet):

    queryset = m.StaffProfile.objects.all()
    serializer_class = s.StaffProfileSerializer
    short_serializer_class = s.ShortStaffProfileSerializer

    def get_queryset(self):
        queryset = self.queryset

        department = self.request.query_params.get('department', None)
        if department is not None:
            queryset = queryset.filter(department__id=department)

        return queryset

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

    @action(
        detail=False, url_path='me', permission_classes=[IsDriverOrEscortUser]
    )
    def me(self, request):

        serializer = s.DriverAppStaffProfileSerializer(
            request.user.profile
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # version 2
    @action(detail=False, url_path='work-status')
    def get_drivers_or_escorts_status(self, request):
        """
        retrieve the driver info
        this api is called in arrange view when user select the driver
        """
        user_type = request.query_params.get('user_type', 'D')
        page = self.paginate_queryset(
            m.StaffProfile.objects.filter(user__user_type=user_type)
        )
        serializer = s.DriverEscortStatusSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    # version 2

    @action(detail=False, url_path='short-staff')
    def short_staff(self, request):
        serializer = s.ShortStaffProfileSerializer(
            self.get_queryset().filter(
                user__user_type__in=[c.USER_TYPE_ADMIN, c.USER_TYPE_STAFF]
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

    @action(detail=False, url_path='in-work-drivers')
    def get_in_work_drivers(self, request):
        """
        get in-work drivers
        """
        page = self.paginate_queryset(
            m.StaffProfile.inwork_drivers.all()
        )
        serializer = s.ShortStaffProfileSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='available-drivers')
    def get_available_drivers(self, request):
        """
        get available drivers
        """
        page = self.paginate_queryset(
            m.StaffProfile.available_drivers.all()
        )
        serializer = s.ShortStaffProfileSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='in-work-escorts')
    def get_in_work_escorts(self, request):
        """
        get in-work escorts
        """
        page = self.paginate_queryset(
            m.StaffProfile.inwork_escorts.all()
        )
        serializer = s.ShortStaffProfileSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='available-escorts')
    def get_available_escorts(self, request):
        """
        get available escorts
        """
        page = self.paginate_queryset(
            m.StaffProfile.available_escorts.all()
        )
        serializer = s.ShortStaffProfileSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='drivers/short')
    def get_short_driver_users(self, request):
        serializer = s.ShortStaffProfileSerializer(
            m.StaffProfile.drivers.all(),
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='escorts/short')
    def get_short_escort_users(self, request):
        serializer = s.ShortStaffProfileSerializer(
            m.StaffProfile.escorts.all(),
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
            'contacts': request.data.pop('contacts')
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
            'contacts': request.data.pop('contacts')
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

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        serializer = s.CustomerAppProfileSerializer(
            request.user.customer_profile
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path='update-me')
    def update_me(self, request):
        customer_profile = request.user.customer_profile

        if request.data.get('mobile', None) is not None:
            customer_profile.mobile = request.data.get('mobile')

        if request.data.get('password', None) is not None:
            request.user.set_password(request.data.get('password'))
            request.user.save()

        customer_profile.save()
        return Response(
            s.CustomerAppProfileSerializer(customer_profile).data,
            status=status.HTTP_200_OK
        )
