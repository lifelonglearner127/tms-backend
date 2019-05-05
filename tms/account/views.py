from rest_framework import status
from rest_framework.response import Response

from ..core.views import StaffViewSet
from .serializers import AuthSerializer, UserSerializer, CustomerSerializer
from .models import User, CustomerProfile


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': AuthSerializer(user, context={'request': request}).data
    }


class UserViewSet(StaffViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CustomerViewSet(StaffViewSet):

    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerSerializer

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
