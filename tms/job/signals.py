from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import Job
from ..notification.models import DriverJobNotification


@receiver(post_save, sender=Job)
def notify_driver(sender, instance, **kwargs):
    message = "A new mission is assigned to you."\
        "Please use {}".format(instance.vehicle)

    DriverJobNotification.objects.create(
        driver=instance.driver,
        message=message
    )
