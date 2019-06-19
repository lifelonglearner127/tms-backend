from django.db import models
from ..hr.models import StaffProfile


class DriverJobNotification(models.Model):

    driver = models.ForeignKey(
        StaffProfile,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    message = models.TextField()

    is_read = models.BooleanField(
        default=False
    )

    def __str__(self):
        return 'Meessage to {}'.format(
            self.driver.user.username
        )
