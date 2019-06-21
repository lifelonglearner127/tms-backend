from django.dispatch import receiver
from django.db.models.signals import post_save
from ..job.models import Job
from ..core.pushy import PushyAPI


@receiver(post_save, sender=Job)
def job_created(sender, instance, created, **kwargs):
    if instance.driver.device_token is None:
        return

    to = [instance.driver.device_token]
    data = {'message': 'New job is assgiend to you'}
    options = {
        'notification': {
            'badge': 1,
            'sound': 'ping.aiff',
            'body': u'New job is assigned to you'
        }
    }

    # Send the push notification with Pushy
    PushyAPI.sendPushNotification(data, to, options)
