from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from ..core import constants as c
from ..core.redis import r

# models
from . import models as m
from .tasks import calculate_job_report, notify_of_job_cancelled


@receiver(post_save, sender=m.Job)
def updated_job(sender, instance, created, **kwargs):

    if instance.progress > c.JOB_PROGRESS_NOT_STARTED:
        r.sadd('jobs', instance.id)

        # set order status to in-progress
        if instance.order.status == c.ORDER_STATUS_PENDING:
            instance.order.status = c.ORDER_STATUS_INPROGRESS
            instance.order.save()

    if instance.progress == c.JOB_PROGRESS_COMPLETE:
        r.srem('jobs', instance.id)
        calculate_job_report.apply_async(
            args=[{
                'job': instance.id,
                'vehicle': instance.vehicle.id,
                'driver': instance.driver.id,
                'escort': instance.escort.id
            }]
        )


@receiver(post_delete, sender=m.Job)
def job_deleted(sender, instance, **kwargs):

    notify_of_job_cancelled.apply_async(
        args=[{
            'job': instance.id,
            'vehicle': instance.vehicle.id,
            'driver': instance.driver.id,
            'escort': instance.escort.id
        }]
    )
