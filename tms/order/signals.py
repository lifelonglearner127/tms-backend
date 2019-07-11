import json
import month
from django.dispatch import receiver
from django.db.models.signals import post_save

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from ..core.pushy import PushyAPI

from ..core import constants as c

# models
from . import models as m
from ..vehicle.models import VehicleUserBind


channel_layer = get_channel_layer()


@receiver(post_save, sender=m.Job)
def notify_driver_of_new_job(sender, instance, created, **kwargs):

    if created:
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

        # send in-app notfication to driver
        message = "A new mission is assigned to you."\
            "Please use {}".format(instance.vehicle.plate_num)
        if instance.driver.channel_name:
            async_to_sync(channel_layer.send)(
                instance.driver.channel_name,
                {
                    'type': 'notify',
                    'data': json.dumps({
                        'msg_type': c.DRIVER_NOTIFICATION_TYPE_JOB,
                        'plate_num': message
                    })
                }
            )

        # send push notification to driver
        if instance.driver.device_token:
            to = [instance.driver.device_token]
            data = {
                'msg_type': c.DRIVER_NOTIFICATION_TYPE_JOB,
                'message': message
            }
            options = {
                'notification': {
                    'badge': 1,
                    'sound': 'ping.aiff',
                    'body': u'New job is assigned to you'
                }
            }

            # Send the push notification with Pushy
            PushyAPI.sendPushNotification(data, to, options)

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
