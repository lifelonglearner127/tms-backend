import json
from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync

from . import models as m
from . import serializers as s
from ..core import constants as c
from ..account.models import User
from ..info.models import Station
from ..order.models import Job


class NotificationConsumer(JsonWebsocketConsumer):
    def connect(self):
        try:
            user_pk = self.scope['url_route']['kwargs']['user_pk']
            self.user = User.objects.get(pk=user_pk)
            self.user.channel_name = self.channel_name
            self.user.save()
            self.accept()
        except User.DoesNotExist:
            self.close()

    def disconnect(self, close_code):
        self.user.channel_name = ''
        self.user.save()

    def receive(self, text_data):
        pass

    def notify(self, event):
        data = json.loads(event['data'])
        msg_type = int(data['msg_type'])
        message = ''

        if msg_type in [
            c.DRIVER_NOTIFICATION_TYPE_ENTER_AREA,
            c.DRIVER_NOTIFICATION_TYPE_EXIT_AREA
        ]:
            plate_num = data['plate_num']
            try:
                station = Station.objects.get(
                    latitude=data['station_pos'][0],
                    longitude=data['station_pos'][1]
                )
                if station.station_type == c.STATION_TYPE_BLACK_DOT:
                    if msg_type == c.DRIVER_NOTIFICATION_TYPE_ENTER_AREA:
                        message = station.notification_message
                    else:
                        message = "Out of this black dot"

                else:
                    job = Job.inprogress.filter(
                        vehicle__plate_num=plate_num,
                        driver=self.user
                    ).first()
                    if job is None or job.route is None:
                        return

                    if station in job.route.stations:
                        if msg_type == c.DRIVER_NOTIFICATION_TYPE_ENTER_AREA:
                            message = "In {}".format(station.name)
                        else:
                            message = "Out of {}".format(station.name)

            except Station.DoesNotExist:
                return
        else:
            message = data['message']

        if message:
            notification = m.Notification.objects.create(
                user=self.user,
                message=message,
                msg_type=msg_type
            )

            self.send_json({
                'content':
                json.dumps(s.NotificationSerializer(notification).data)
            })


class PositionConsumer(JsonWebsocketConsumer):
    def connect(self):
        try:
            user_pk = self.scope['url_route']['kwargs']['user_pk']
            self.user = User.objects.get(pk=user_pk)
            async_to_sync(self.channel_layer.group_add)(
                'position',
                self.channel_name
            )

            self.accept()
        except User.DoesNotExist:
            self.close()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            'position',
            self.channel_name
        )

    def receive(self, text_data):
        pass

    def notify_position(self, event):
        self.send_json({
            'content': event['data']
        })
