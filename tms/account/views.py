from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from ..core.constants import USER_DOCUMENT_TYPE
from ..core.views import StaffViewSet, ChoicesView
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

    @action(detail=False)
    def short(self, request):
        serializer = s.ShortStaffProfileSerializer(
            m.StaffProfile.objects.all(),
            many=True
        )
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
            'associated_with': request.data.pop('associated_with')
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
            'associated_with': request.data.pop('associated_with')
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

    @action(detail=False)
    def short(self, request):
        serializer = s.ShortCustomerProfileSerializer(
            m.CustomerProfile.objects.all(),
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class StaffDocumentViewSet(StaffViewSet):
    """
    Viewset for document
    """
    serializer_class = s.StaffDocumentSerializer

    def get_queryset(self):
        return m.StaffDocument.objects.filter(
            staff__id=self.kwargs['staff_pk']
        )

    def create(self, request, staff_pk=None):
        data = request.data.copy()
        data.setdefault('staff', staff_pk)

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )

    def update(self, request, staff_pk=None, pk=None):
        data = request.data.copy()
        data.setdefault('staff', staff_pk)

        instance = self.get_object()
        serializer = self.serializer_class(
            instance,
            data=data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data, status=status.HTTP_200_OK
        )


class UserDocumentTypeAPIView(ChoicesView):
    """
    APIView for returning product categories
    """
    static_choices = USER_DOCUMENT_TYPE
