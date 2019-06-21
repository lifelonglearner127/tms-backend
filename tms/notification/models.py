from django.db import models
from ..account.models import User


class DriverJobNotification(models.Model):

    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    message = models.TextField()

    is_read = models.BooleanField(
        default=False
    )

    def __str__(self):
        return 'Meessage to {}'.format(
            self.user.username
        )
