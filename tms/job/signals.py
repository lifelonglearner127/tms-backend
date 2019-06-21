from django.dispatch import receiver
from django.db.models.signals import post_save

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from . import models as m
from ..account.models import User
from ..core import constants as c
from ..notification.models import DriverJobNotification


channel_layer = get_channel_layer()


@receiver(post_save, sender=m.Job)
def notify_driver_of_new_job(sender, instance, **kwargs):
    message = "A new mission is assigned to you."\
        "Please use {}".format(instance.vehicle)

    DriverJobNotification.objects.create(
        driver=instance.driver,
        message=message
    )

    if instance.driver.channel_name is not None:
        async_to_sync(channel_layer.send)(
            instance.driver.channel_name,
            {
                'type': 'notify',
                'msg_type': c.DRIVER_NOTIFICATION_NEW_JOB,
                'msg': message
            }
        )


@receiver(post_save, sender=m.ParkingRequest)
def notify_staff_of_parking_request(sender, instance, **kwargs):

    admin = User.objects.get(role=c.USER_ROLE_ADMIN)[0]
    if admin.channel_name is not None:
        async_to_sync(channel_layer.send)(
            admin.channel_name,
            {
                'type': 'notify',
                'msg_type': c.STAFF_NOTIFICATION_PARKING_REQUEST,
                'msg': 'Parking Request'
            }
        )


@receiver(post_save, sender=m.DriverChangeRequest)
def notify_staff_of_driver_change_request(sender, instance, **kwargs):

    admin = User.objects.get(role=c.USER_ROLE_ADMIN)[0]
    if admin.channel_name is not None:
        async_to_sync(channel_layer.send)(
            admin.channel_name,
            {
                'type': 'notify',
                'msg_type': c.STAFF_NOTIFICATION_DRIVER_CHANGE_REQUEST,
                'msg': 'Driver Change Request'
            }
        )


@receiver(post_save, sender=m.DriverChangeRequest)
def notify_staff_of_escort_change_request(sender, instance, **kwargs):

    admin = User.objects.get(role=c.USER_ROLE_ADMIN)[0]
    if admin.channel_name is not None:
        async_to_sync(channel_layer.send)(
            admin.channel_name,
            {
                'type': 'notify',
                'msg_type': c.STAFF_NOTIFICATION_ESCORT_CHANGE_REQUEST,
                'msg': 'Escort Change Request'
            }
        )
