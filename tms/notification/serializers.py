from rest_framework import serializers
from . import models as m


class DriverJobNotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.DriverJobNotification
        fields = (
            'id', 'message', 'is_read'
        )
