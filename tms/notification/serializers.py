from rest_framework import serializers
from . import models as m


class NotificationSerializer(serializers.ModelSerializer):

    message = serializers.JSONField()

    class Meta:
        model = m.Notification
        exclude = ('user', )


class ReadNotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Notification
        fields = ('is_read', )
