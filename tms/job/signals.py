from django.dispatch import receiver
from django.db.models.signals import post_save

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Job
from ..core import constants as c
from ..notification.models import DriverJobNotification


channel_layer = get_channel_layer()


@receiver(post_save, sender=Job)
def notify_driver(sender, instance, **kwargs):
    message = "A new mission is assigned to you."\
        "Please use {}".format(instance.vehicle)

    DriverJobNotification.objects.create(
        driver=instance.driver,
        message=message
    )

    if instance.driver.user.channel_name is not None:
        async_to_sync(channel_layer.send)(
            instance.driver.user.channel_name,
            {
                'type': 'notify',
                'msg_type': c.DRIVER_NOTIFICATION_NEW_JOB,
                'msg': message
            }
        )
