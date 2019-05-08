from rest_framework import status
from rest_framework.response import Response

from ..core.views import StaffViewSet, ShortAPIView
from . import models as m
from . import serializers as s


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': s.AuthSerializer(user, context={'request': request}).data
    }


class UserViewSet(StaffViewSet):
    """
    Viewset for User
    """
    queryset = m.User.objects.all()
    serializer_class = s.UserSerializer


class StaffProfileViewSet(StaffViewSet):
    """
    Viewset for Staff
    """
    queryset = m.StaffProfile.objects.all()
    serializer_class = s.StaffProfileSerializer

    def create(self, request):
        context = {
            'user': request.data.pop('user')
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
            'user': request.data.pop('user')
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


class CustomerProfileViewSet(StaffViewSet):
    """
    Viewset for Customer
    """
    queryset = m.CustomerProfile.objects.all()
    serializer_class = s.CustomerProfileSerializer

    def create(self, request):
        context = {
            'user': request.data.pop('user'),
            'associated': request.data.pop('associated')
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
            'associated': request.data.pop('associated')
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


class ShortStaffAPIView(ShortAPIView):
    """
    View to list short data of customer profiles
    """
    serializer_class = s.ShortUserSerializer

    def get_queryset(self):
        return m.User.staffs.all()


class ShortCustomerAPIView(ShortAPIView):
    """
    View to list short data of customer profiles
    """
    serializer_class = s.ShortUserSerializer

    def get_queryset(self):
        return m.User.customers.all()
