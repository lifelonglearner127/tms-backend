import json
from django.dispatch import receiver
from django.db.models.signals import post_save
from fieldsignals import pre_save_changed
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# constants
from ..core import constants as c

# models
from . import models as m
from ..account.models import User
from ..notification.models import Notification

# serializers
from ..notification.serializers import NotificationSerializer


channel_layer = get_channel_layer()


@receiver(post_save, sender=m.ParkingRequest)
def notify_staff_of_parking_request(sender, instance, **kwargs):
    message = "{} created {} parking request."\
        "Please approve it".format(instance.driver, instance.vehicle)

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


@receiver(post_save, sender=m.DriverChangeRequest)
def notify_staff_of_driver_change_request(sender, instance, **kwargs):
    pass


@receiver(post_save, sender=m.DriverChangeRequest)
def notify_staff_of_escort_change_request(sender, instance, **kwargs):
    pass


@receiver(post_save, sender=m.RestRequest)
def notify_staff_of_rest_request(sender, instance, created, **kwargs):

    if created:
        admin = User.objects.filter(role=c.USER_ROLE_ADMIN)[0]
        if admin.channel_name is not None:
            message = "{} make an rest request."\
                "Please check and approve.".format(instance.user.name)

            async_to_sync(channel_layer.send)(
                admin.channel_name,
                {
                    'type': 'notify',
                    'data': json.dumps({
                        'msg_type': c.STAFF_NOTIFICATION_REST_REQUEST,
                        'message': message
                    })
                }
            )


@receiver(
    pre_save_changed, sender=m.RestRequest,
    fields=['approved']
)
def notify_staff_of_rest_request_result(sender, instance,
                                        changed_fields=None, **kwargs):

    for field, (old, new) in changed_fields.items():
        if field.name == 'approved' and instance.user.channel_name:
            if new:
                msg_type = c.STAFF_NOTIFICATION_REST_REQUEST_APPROVED
                message = "Your rest request from {} to {} was "\
                    "approved".format(instance.from_date, instance.to_date)

            else:
                msg_type = c.STAFF_NOTIFICATION_REST_REQUEST_DECLINE
                message = "Your rest request from {} to {} was "\
                    "declined".format(instance.from_date, instance.to_date)

            async_to_sync(channel_layer.send)(
                instance.user.channel_name,
                {
                    'type': 'notify',
                    'data': json.dumps({
                        'msg_type': msg_type,
                        'message': message
                    })
                }
            )
