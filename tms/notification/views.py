from rest_framework import mixins, viewsets

from . import serializers as s
from ..core.permissions import IsDriverOrEscortUser


class DriverNotificationViewSet(mixins.RetrieveModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    permission_classes = [IsDriverOrEscortUser]
    serializer_class = s.DriverJobNotificationSerializer

    def get_queryset(self):
        return self.request.user.driver_profile.notifications.all()
