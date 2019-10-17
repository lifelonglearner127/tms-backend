from rest_framework import serializers
from . import models as m
from ..account.serializers import UserNameSerializer


class NotificationSerializer(serializers.ModelSerializer):

    message = serializers.JSONField()

    class Meta:
        model = m.Notification
        exclude = ('user', )


class ReadNotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Notification
        fields = ('is_read', )


class EventSerializer(serializers.ModelSerializer):

    vehicle = serializers.SerializerMethodField()
    driver = UserNameSerializer(read_only=True)

    class Meta:
        model = m.Event
        fields = '__all__'

    def get_vehicle(self, instance):
        ret = {}
        ret['id'] = instance.vehicle.id
        if instance.is_head:
            ret['plate_num'] = instance.vehicle.plate_num
        else:
            ret['plate_num'] = instance.vehicle.plate_num_2

        return ret
