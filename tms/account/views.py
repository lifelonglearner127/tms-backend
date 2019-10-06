from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response

from ..core import constants as c
from ..core.serializers import ChoiceSerializer
from ..core.views import TMSViewSet
from . import models as m
from . import serializers as s


class JWTAPIView(APIView):
    """
    Base API View that various JWT interactions inherit from.
    """
    permission_classes = ()
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data.get('user') or request.user
            token = serializer.validated_data.get('token')
            return Response({
                'token': token,
                'user': s.AuthSerializer(user).data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ObtainJWTAPIView(JWTAPIView):
    """
    API View that receives a POST with username and password and user user_type
    Returns a JSON Web Token with user data
    """
    serializer_class = s.ObtainJWTSerializer


class VerifyJWTAPIView(JWTAPIView):
    """
    API View that checks the veracity of a token, returning the token and
    user data if it is valid.
    """
    serializer_class = s.VerifyJWTSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    Viewset for User
    """
    queryset = m.User.objects.all()
    serializer_class = s.UserSerializer
    short_serializer_class = s.ShortUserSerializer

    # version 2
    @action(detail=False, url_path='short/by-types')
    def get_short_users_by_types(self, request):
        """
        retrieve users by its user types.
        """
        user_types = request.query_params.get('user_types', [])
        queryset = self.queryset
        if len(user_types) > 0:
            queryset = queryset.filter(user_type__in=user_types)

        return Response(
            s.ShortUserSerializer(queryset, many=True).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path="me")
    def update_me(self, request):
        username = request.data.get('username', None)
        if username is not None:
            if m.User.objects.exclude(id=request.user.id).filter(username=username).exists():
                return Response(
                    {'username': 'Duplicate username'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                request.user.username = username

        password = request.data.get('password', None)
        if password is not None:
            request.user.set_password(password)

        mobile = request.data.get('mobile', None)
        if mobile is not None:
            if m.User.objects.exclude(id=request.user.id).filter(mobile=mobile).exists():
                return Response(
                    {'mobile': 'Duplicate mobile'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                request.user.mobile = mobile

        request.user.save()

        data = request.data
        data['user_type'] = request.user.user_type

        serializer = s.ObtainJWTSerializer(data=data)

        if serializer.is_valid():
            user = serializer.validated_data.get('user') or request.user
            token = serializer.validated_data.get('token')
            return Response({
                'token': token,
                'user': s.AuthSerializer(user).data
            }, status=status.HTTP_200_OK)

        return Response({'error': 'error occured while saving new credentials'}, status=status.HTTP_200_OK)

    @action(detail=False, url_path="types")
    def get_user_types(self, request):
        serializer = ChoiceSerializer(
            [{'value': x, 'text': y} for (x, y) in c.USER_TYPE],
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="member-types")
    def get_member_types(self, request):
        serializer = ChoiceSerializer(
            [
                {'value': x, 'text': y} for (x, y) in c.USER_TYPE
                if x != c.USER_TYPE_CUSTOMER
            ],
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='company-members/short')
    def get_short_company_members(self, request):
        serializer = s.ShortCompanyMemberSerializer(
            m.User.companymembers.all(),
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='company-member-list')
    def get_short_company_members_with_pagination(self, request):
        serializer = s.ShortCompanyMemberSerializer(
            self.paginate_queryset(m.User.companymembers.all()),
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='staffs/short')
    def get_short_staff_users(self, request):
        serializer = s.ShortUserSerializer(
            m.User.staffs.all(),
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='staff-list')
    def get_short_staff_users_with_pagination(self, request):
        serializer = s.ShortUserSerializer(
            self.paginate_queryset(m.User.staffs.all()),
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='drivers/short')
    def get_short_driver_users(self, request):
        serializer = s.ShortUserSerializer(
            m.User.drivers.all(),
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='escorts/short')
    def get_short_escort_users(self, request):
        serializer = s.ShortUserSerializer(
            m.User.escorts.all(),
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="wheels/short")
    def get_wheels_users(self, request):
        serializer = s.ShortUserWithDepartmentSerializer(
            self.paginate_queryset(m.User.wheels.all()),
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='customers/short')
    def get_short_customer_users(self, request):
        serializer = s.ShortUserSerializer(
            m.User.customers.all(),
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class UserPermissionViewSet(TMSViewSet):

    queryset = m.UserPermission.objects.all()
    serializer_class = s.UserPermissionSerializer
    short_serializer_class = s.ShortUserPermissionSerializer

    def create(self, request):
        data = request.data
        permission_data = request.data.pop('permissions')
        permissions = []
        for key, actions in permission_data.items():
            for action_name in actions:
                obj, created = m.Permission.objects.get_or_create(
                    page=key,
                    action=action_name
                )
                permissions.append(obj.id)

        data['permissions'] = permissions
        serializer = s.UserPermissionSerializer(
            data=data
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        instance = self.get_object()
        data = request.data
        permission_data = request.data.pop('permissions')
        permissions = []
        for key, actions in permission_data.items():
            for action_name in actions:
                obj, created = m.Permission.objects.get_or_create(
                    page=key,
                    action=action_name
                )
                permissions.append(obj.id)

        data['permissions'] = permissions
        serializer = s.UserPermissionSerializer(
            instance, data=data, partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
