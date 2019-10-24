from django.dispatch import receiver
from django.db.models.signals import post_save

from ..core import constants as c
from ..core.redis import r

# models
from . import models as m


@receiver(post_save, sender=m.Job)
def updated_job(sender, instance, created, **kwargs):

    if created:
        pass

    if instance.progress > c.JOB_PROGRESS_NOT_STARTED:
        r.sadd('jobs', instance.id)

        # set order status to in-progress
        if instance.order.status == c.ORDER_STATUS_PENDING:
            instance.order.status = c.ORDER_STATUS_INPROGRESS
            instance.order.save()

    # if instance.progress == c.JOB_PROGRESS_COMPLETE:
    #     r.srem('jobs', instance.id)
    #     calculate_job_report.apply_async(
    #         args=[{
    #             'job': instance.id,
    #             'vehicle': instance.vehicle.id,
    #             'driver': instance.driver.id,
    #             'escort': instance.escort.id
    #         }]
    #     )


# Job delete notifications; when the job is deleted, driver, escort should be notified of the changes
# @receiver(pre_delete, sender=m.Job)
# def job_deleted(sender, instance, **kwargs):

#     notify_of_job_deleted.apply_async(
#         args=[{
#             'job': instance.id,
#             'vehicle': instance.vehicle.id,
#             'driver': instance.associated_drivers.first().id,
#             'escort': instance.associated_escorts.first().id
#         }]
#     )
