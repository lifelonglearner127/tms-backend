from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from . import serializers as s
from .permissions import IsMyNotification


class NotificationViewSet(mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    permission_classes = [IsMyNotification]
    serializer_class = s.NotificationSerializer

    def get_queryset(self):
        return self.request.user.notifications.all()

    @action(detail=True, methods=['post'], url_path='read')
    def read_notification(self, request, pk=None):
        instance = self.get_object()
        serializer = s.ReadNotificationSerializer(
            instance,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_notification_count(self, request):
        return Response(
            {
                'count':
                request.user.notifications.filter(is_read=False).count()
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], url_path='read-count')
    def read_notification_count(self, request):
        return Response(
            {
                'count':
                request.user.notifications.filter(is_read=True).count()
            },
            status=status.HTTP_200_OK
        )
