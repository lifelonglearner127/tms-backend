from rest_framework import status
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


class UserViewSet(TMSViewSet):
    """
    Viewset for User
    """
    queryset = m.User.objects.all()
    serializer_class = s.UserSerializer

    @action(detail=False, url_path="roles")
    def get_user_roles(self, request):
        serializer = ChoiceSerializer(
            [{'value': x, 'text': y} for (x, y) in c.USER_ROLE],
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="member-roles")
    def get_member_roles(self, request):
        serializer = ChoiceSerializer(
            [
                {'value': x, 'text': y} for (x, y) in c.USER_ROLE
                if x != c.USER_ROLE_CUSTOMER
            ],
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
