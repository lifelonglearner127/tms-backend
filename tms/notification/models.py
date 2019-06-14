from django.db import models
from ..account.models import DriverProfile


class DriverJobNotification(models.Model):

    driver = models.ForeignKey(
        DriverProfile,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    message = models.TextField()

    is_read = models.BooleanField(
        default=False
    )

    def __str__(self):
        return 'Meessage to {} at {}'.format(
            self.driver.user.username, self.sent
        )
