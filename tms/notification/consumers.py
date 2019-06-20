from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
from ..account.models import User


class NotificationConsumer(JsonWebsocketConsumer):
    def connect(self):
        try:
            user_pk = self.scope['url_route']['kwargs']['user_pk']
            self.user = User.objects.get(pk=user_pk)
            self.user.channel_name = self.channel_name
            self.user.save()
            self.accept()
        except User.objects.DoesNotExists:
            self.close()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        pass

    def notify(self, event):
        self.send_json({
            'content': event['msg_type'],
            'msg': event['msg']
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
        except User.objects.DoesNotExists:
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
