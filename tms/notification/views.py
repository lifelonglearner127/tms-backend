from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from . import serializers as s
from ..core.permissions import IsDriverOrEscortUser


class DriverJobNotificationViewSet(mixins.RetrieveModelMixin,
                                   mixins.ListModelMixin,
                                   viewsets.GenericViewSet):
    permission_classes = [IsDriverOrEscortUser]
    serializer_class = s.DriverJobNotificationSerializer

    def get_queryset(self):
        return self.request.user.driver_profile.notifications.all()

    @action(detail=True, methods=['get'], url_path='read')
    def read_notification(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()

        return Response(
            self.serializer_class(notification).data,
            status=status.HTTP_200_OK
        )
