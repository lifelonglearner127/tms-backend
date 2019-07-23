import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer


from ..core import constants as c

# models
from . import models as m
from ..account.models import User
from ..info.models import Station
from ..order.models import Job, JobStation

# serializers
from . import serializers as s


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        try:
            user_pk = self.scope['url_route']['kwargs']['user_pk']
            self.user = User.objects.get(pk=user_pk)
            self.user.channel_name = self.channel_name
            self.user.save()
            await self.accept()
        except User.DoesNotExist:
            await self.close()

    async def disconnect(self, close_code):
        self.user.channel_name = ''
        self.user.save()

    def receive(self, text_data):
        pass

    async def notify(self, event):
        data = json.loads(event['data'])
        msg_type = int(data['msg_type'])

        if msg_type in [
            c.DRIVER_NOTIFICATION_TYPE_ENTER_BLACK_DOT,
            c.DRIVER_NOTIFICATION_TYPE_EXIT_BLACK_DOT,
            c.DRIVER_NOTIFICATION_TYPE_ENTER_STATION,
            c.DRIVER_NOTIFICATION_TYPE_EXIT_STATION
        ]:
            station = Station.objects.get(id=data['station_id'])
            message = {
                'name': station.name,
                'address': station.address
            }

            if station.notification_message:
                message['notification'] = station.notification_message

            notification = m.Notification.objects.create(
                user=self.user,
                message=message,
                msg_type=msg_type
            )

            if msg_type == c.DRIVER_NOTIFICATION_TYPE_ENTER_STATION:
                job = Job.objects.get(id=data['job_id'])
                job_station = JobStation.objects.get(job=job, station=station)
                expected_progress = job_station.step * 4 + 2

                if job.progress != expected_progress:
                    job.progress = expected_progress
                    job.save()

            elif msg_type == c.DRIVER_NOTIFICATION_TYPE_EXIT_STATION:
                job = Job.objects.get(id=data['job_id'])
                if job.order.is_same_station:
                    expected_progress = 10 + job_station.step * 4
                else:
                    expected_progress = 6 + job_station.step * 4

                if job.progress != expected_progress:
                    job.progress = expected_progress
                    job.save()

            await self.send_json({
                'content':
                json.dumps(s.NotificationSerializer(notification).data)
            })
        else:
            await self.send_json({
                'content': event['data']
            })


class PositionConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        try:
            user_pk = self.scope['url_route']['kwargs']['user_pk']
            self.user = User.objects.get(pk=user_pk)
            await self.channel_layer.group_add(
                'position',
                self.channel_name
            )

            await self.accept()
        except User.DoesNotExist:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            'position',
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def notify_position(self, event):
        await self.send_json({
            'content': event['data']
        })
