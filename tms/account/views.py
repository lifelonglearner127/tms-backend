from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from ..core import constants as c
from ..core.views import StaffViewSet, ChoicesView
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
    API View that receives a POST with username and password and user role
    Returns a JSON Web Token with user data
    """
    serializer_class = s.ObtainJWTSerializer


class VerifyJWTAPIView(JWTAPIView):
    """
    API View that checks the veracity of a token, returning the token and
    user data if it is valid.
    """
    serializer_class = s.VerifyJWTSerializer


class UserViewSet(StaffViewSet):
    """
    Viewset for User
    """
    queryset = m.User.objects.all()
    serializer_class = s.UserSerializer


class BaseStaffProfileViewSet(StaffViewSet):

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


class StaffProfileViewSet(BaseStaffProfileViewSet):
    """
    Viewset for Staff
    """
    queryset = m.StaffProfile.objects.all()
    serializer_class = s.StaffProfileSerializer
    short_serializer_class = s.ShortStaffProfileSerializer


class DriverProfileViewSet(BaseStaffProfileViewSet):
    """
    Viewset for Staff
    """
    queryset = m.DriverProfile.objects.all()
    serializer_class = s.DriverProfileSerializer
    short_serializer_class = s.ShortDriverProfileSerializer


class EscortProfileViewSet(BaseStaffProfileViewSet):
    """
    Viewset for Staff
    """
    queryset = m.EscortProfile.objects.all()
    serializer_class = s.EscortProfileSerializer
    short_serializer_class = s.ShortEscortProfileSerializer


class CustomerProfileViewSet(StaffViewSet):
    """
    Viewset for Customer
    """
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
    static_choices = c.USER_DOCUMENT_TYPE


class CompanyMemberViewSet(StaffViewSet):
    """
    """
    serializer_class = s.CompanyMemberSerializer

    def get_queryset(self):
        return m.User.companymembers.all()

    def create(self, request):
        context = {
            'profile': request.data.pop('profile')
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
            'profile': request.data.pop('profile')
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
