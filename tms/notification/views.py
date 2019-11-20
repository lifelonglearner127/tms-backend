from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models as m
from . import serializers as s
from .permissions import IsMyNotification


class NotificationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsMyNotification]
    serializer_class = s.NotificationSerializer

    def get_queryset(self):
        return self.request.user.notifications.filter(is_deleted=False)

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
                request.user.notifications.filter(is_deleted=False, is_read=False).count()
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], url_path='read-count')
    def read_notification_count(self, request):
        return Response(
            {
                'count':
                request.user.notifications.filter(is_deleted=False, is_read=True).count()
            },
            status=status.HTTP_200_OK
        )

    def destroy(self, request, pk=None):
        job = self.get_object()
        job.is_deleted = True
        job.save()

        return Response(
            {
                'msg': 'successfully deleted '
            },
            status=status.HTTP_200_OK
        )


class EventViewSets(viewsets.ModelViewSet):

    queryset = m.Event.objects.all()
    serializer_class = s.EventSerializer


class G7MQTTEventViewSets(viewsets.ModelViewSet):

    queryset = m.G7MQTTEvent.objects.all()
    serializer_class = s.G7MQTTEventSerializer

    def get_queryset(self):
        queryset = self.queryset

        event_type = self.request.query_params.get('event_type', None)

        if event_type:
            queryset = queryset.filter(event_type=int(event_type))

        return queryset
