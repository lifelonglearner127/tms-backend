from rest_framework import serializers
from . import models as m
from ..core import constants as c
from ..core.serializers import TMSChoiceField
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

    event_type = TMSChoiceField(choices=c.EVENT_TYPE)
    vehicle = serializers.SerializerMethodField()
    driver = UserNameSerializer(read_only=True)

    class Meta:
        model = m.Event
        fields = '__all__'

    def get_vehicle(self, instance):
        ret = {}
        if instance.vehicle is None:
            return None

        ret['id'] = instance.vehicle.id
        if instance.is_head:
            ret['plate_num'] = instance.vehicle.plate_num
        else:
            ret['plate_num'] = instance.vehicle.plate_num_2

        return ret


class G7MQTTEventSerializer(serializers.ModelSerializer):

    vehicle = serializers.CharField(source='vehicle.plate_num')
    driver = serializers.SerializerMethodField()
    escort = serializers.SerializerMethodField()
    event_type = TMSChoiceField(choices=c.MQTT_EVENT_TYPE)
    push_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = m.G7MQTTEvent
        fields = '__all__'

    def get_driver(self, instance):
        if instance.driver:
            return {
                'name': instance.driver.name,
                'mobile': instance.driver.mobile
            }
        else:
            return {
                'name': '-',
                'mobile': '-',
            }

    def get_escort(self, instance):
        if instance.escort:
            return {
                'name': instance.escort.name,
                'mobile': instance.escort.mobile
            }
        else:
            return {
                'name': '-',
                'mobile': '-',
            }
