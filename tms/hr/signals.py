from django.dispatch import receiver
from django.db.models.signals import post_save

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import RestRequest
from ..core import constants as c
from ..account.models import User


channel_layer = get_channel_layer()


@receiver(post_save, sender=RestRequest)
def notify_staff_of_rest_request(sender, instance, **kwargs):
    admin = User.objects.filter(role=c.USER_ROLE_ADMIN)[0]
    if admin.channel_name is not None:
        async_to_sync(channel_layer.send)(
            admin.channel_name,
            {
                'type': 'notify',
                'msg_type': c.STAFF_NOTIFICATION_REST_REQUEST,
                'msg': 'Rest Request'
            }
        )
