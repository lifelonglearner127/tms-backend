import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer

# models
from ..account.models import User
from ..order.models import Order


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


class CustomerJobPositionConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        try:
            user_pk = self.scope['url_route']['kwargs']['user_pk']
            self.user = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            await self.close()

        try:
            order_pk = self.scope['url_route']['kwargs']['order_pk']
            order = Order.objects.get(pk=order_pk)

            self.vehicles = order.jobs.filter(progress__gt=1).values_list(
                'vehicle__plate_num', flat=True
            )

            await self.channel_layer.group_add(
                'position',
                self.channel_name
            )

            await self.accept()
        except Order.DoesNotExist:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            'position',
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def notify_position(self, event):
        data = event['data']
        for vehicle in data:
            if vehicle['plateNum'] not in self.vehicles:
                data.remote(vehicle)

        await self.send_json({
            'content': json.dumps(data)
        })
