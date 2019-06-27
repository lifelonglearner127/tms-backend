import json
import month
from django.dispatch import receiver
from django.db.models.signals import post_save

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from . import models as m
from ..core import constants as c
from ..account.models import User
from ..notification.models import Notification
from ..notification.serializers import NotificationSerializer
from ..vehicle.models import VehicleUserBind


channel_layer = get_channel_layer()


@receiver(post_save, sender=m.Job)
def notify_driver_of_new_job(sender, instance, **kwargs):

    if instance.progress == c.JOB_PROGRESS_NOT_STARTED:
        # bind vehicle, driver, escort
        if not VehicleUserBind.binds_by_admin.filter(
            vehicle=instance.vehicle,
            driver=instance.driver,
            escort=instance.escort
        ).exists():
            VehicleUserBind.objects.get_or_create(
                vehicle=instance.vehicle,
                driver=instance.driver,
                escort=instance.escort,
                bind_method=c.VEHICLE_USER_BIND_METHOD_BY_JOB
            )

        # send notfication to driver
        if instance.driver.channel_name is not None:
            async_to_sync(channel_layer.send)(
                instance.driver.channel_name,
                {
                    'type': 'notify',
                    'data': json.dumps({
                        'msg_type': c.DRIVER_NOTIFICATION_TYPE_JOB,
                        'plate_num': instance.vehicle.plate_num
                    })
                }
            )

    elif instance.progress == c.JOB_PROGRESS_COMPLETE:
        # unbind vehicle, driver, escort
        if not VehicleUserBind.binds_by_admin.filter(
            vehicle=instance.vehicle,
            driver=instance.driver,
            escort=instance.escort
        ).exists():
            try:
                vehicle_bind = VehicleUserBind.objects.get(
                    vehicle=instance.vehicle,
                    driver=instance.driver,
                    escort=instance.escort,
                    bind_method=c.VEHICLE_USER_BIND_METHOD_BY_JOB
                )
                vehicle_bind.delete()
            except VehicleUserBind.DoesNotExist:
                pass

        # update job report
        job_year = instance.finished_on.year
        job_month = instance.finished_on.month
        try:
            job_report = m.JobReport.objects.get(
                driver=instance.driver,
                month=month.Month(job_year, job_month)
            )
            job_report.total_mileage = \
                job_report.total_mileage + instance.total_mileage
            job_report.empty_mileage = \
                job_report.empty_mileage + instance.empty_mileage
            job_report.heavy_mileage = \
                job_report.heavy_mileage + instance.heavy_mileage
            job_report.highway_mileage = \
                job_report.highway_mileage + instance.highway_mileage
            job_report.normalway_mileage = \
                job_report.normalway_mileage + instance.normalway_mileage

            job_report.save()
        except m.JobReport.DoesNotExist:
            job_report = m.JobReport.objects.create(
                driver=instance.driver,
                month=month.Month(job_year, job_month),
                total_mileage=instance.total_mileage,
                empty_mileage=instance.empty_mileage,
                heavy_mileage=instance.heavy_mileage,
                highway_mileage=instance.highway_mileage,
                normalway_mileage=instance.normalway_mileage
            )


@receiver(post_save, sender=m.ParkingRequest)
def notify_staff_of_parking_request(sender, instance, **kwargs):
    message = "{} created {} parking request."\
        "Please approve it".format(instance.driver, instance.vehicle)

    admin = User.objects.get(role=c.USER_ROLE_ADMIN)[0]
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
