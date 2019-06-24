import json
from django.dispatch import receiver
from django.db.models.signals import post_save

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import RestRequest
from ..core import constants as c
from ..account.models import User
from ..notification.models import Notification
from ..notification.serializers import NotificationSerializer


channel_layer = get_channel_layer()


@receiver(post_save, sender=RestRequest)
def notify_staff_of_rest_request(sender, instance, **kwargs):

    message = "{} make an rest request."\
        "Please check and approve.".format(instance.user)
    admin = User.objects.filter(role=c.USER_ROLE_ADMIN)[0]
    notification = Notification.objects.create(
        user=admin,
        message=message,
        msg_type=c.DRIVER_NOTIFICATION_TYPE_JOB
    )
    if admin.channel_name is not None:
        async_to_sync(channel_layer.send)(
            admin.channel_name,
            {
                'type': 'notify',
                'data': json.dumps(NotificationSerializer(notification).data)
            }
        )
