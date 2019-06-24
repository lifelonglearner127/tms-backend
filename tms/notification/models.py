from django.db import models
from ..core import constants as c
from ..account.models import User
from . import managers


class Notification(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    msg_type = models.PositiveIntegerField(
        choices=c.NOTIFICATION_TYPE,
        default=c.DRIVER_NOTIFICATION_TYPE_JOB
    )

    message = models.TextField()

    is_read = models.BooleanField(
        default=False
    )

    sent_on = models.DateTimeField(
        auto_now_add=True
    )

    objects = models.Manager()
    unreads = managers.UnreadNotificationManager()
    reads = managers.ReadNotificationManager()

    class Meta:
        ordering = (
            'is_read', '-sent_on'
        )

    def __str__(self):
        return 'Meessage to {}'.format(
            self.user.username
        )
