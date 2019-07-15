import json
import month
from django.shortcuts import get_object_or_404
from config.celery import app
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from ..core.pushy import PushyAPI
from ..core import constants as c

# models
from . import models as m
from ..account.models import User
from ..notification.models import Notification
from ..vehicle.models import Vehicle, VehicleUserBind

# serializers
from ..notification.serializers import NotificationSerializer


channel_layer = get_channel_layer()


@app.task
def notify_new_job(context):
    """
    Send notificatio when a new job is created
    """
    vehicle = get_object_or_404(Vehicle, id=context['vehicle'])
    driver = get_object_or_404(User, id=context['driver'])
    escort = get_object_or_404(User, id=context['escort'])

    # bind vehicle, driver, escort
    if not VehicleUserBind.binds_by_admin.filter(
        vehicle=vehicle,
        driver=driver,
        escort=escort
    ).exists():
        VehicleUserBind.objects.get_or_create(
            vehicle=vehicle,
            driver=driver,
            escort=escort,
            bind_method=c.VEHICLE_USER_BIND_METHOD_BY_JOB
        )

    # set the vehicle status to in-work
    vehicle.status = c.VEHICLE_STATUS_INWORK
    vehicle.save()

    # set the driver & escrot to in-work
    driver.profile.status = c.WORK_STATUS_DRIVING
    escort.profile.status = c.WORK_STATUS_DRIVING
    driver.profile.save()
    escort.profile.save()

    # send in-app notfication to driver & escort
    message = "A new mission is assigned to you."\
        "Please use {}".format(vehicle.plate_num)

    driver_notification = Notification.objects.create(
        user=driver,
        message=message,
        msg_type=c.DRIVER_NOTIFICATION_TYPE_JOB
    )

    escort_notification = Notification.objects.create(
        user=escort,
        message=message,
        msg_type=c.DRIVER_NOTIFICATION_TYPE_JOB
    )

    if driver.channel_name:
        async_to_sync(channel_layer.send)(
            driver.channel_name,
            {
                'type': 'notify',
                'data': json.dumps(
                    NotificationSerializer(driver_notification).data
                )
            }
        )

    if escort.channel_name:
        async_to_sync(channel_layer.send)(
            driver.channel_name,
            {
                'type': 'notify',
                'data': json.dumps(
                    NotificationSerializer(escort_notification).data
                )
            }
        )

    # send push notification to driver & escort
    if driver.device_token:
        to = [driver.device_token]
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


@app.task
def calculate_job_report(context):
    job = get_object_or_404(m.Job, id=context['id'])
    vehicle = get_object_or_404(Vehicle, id=context['vehicle'])
    driver = get_object_or_404(User, id=context['driver'])
    escort = get_object_or_404(User, id=context['escort'])

    # unbind vehicle, driver, escort
    if not VehicleUserBind.binds_by_admin.filter(
        vehicle=vehicle,
        driver=driver,
        escort=escort
    ).exists():
        try:
            vehicle_bind = VehicleUserBind.objects.get(
                vehicle=vehicle,
                driver=driver,
                escort=escort,
                bind_method=c.VEHICLE_USER_BIND_METHOD_BY_JOB
            )
            vehicle_bind.delete()
        except VehicleUserBind.DoesNotExist:
            pass

    # set the vehicle status to available
    vehicle.status = c.VEHICLE_STATUS_AVAILABLE
    vehicle.save()

    # set the driver & escrot to in-work
    driver.profile.status = c.WORK_STATUS_AVAILABLE
    escort.profile.status = c.WORK_STATUS_AVAILABLE
    driver.profile.save()
    escort.profile.save()

    # update job report
    job_year = job.finished_on.year
    job_month = job.finished_on.month
    try:
        job_report = m.JobReport.objects.get(
            driver=driver,
            month=month.Month(job_year, job_month)
        )
        job_report.total_mileage = \
            job_report.total_mileage + job.total_mileage
        job_report.empty_mileage = \
            job_report.empty_mileage + job.empty_mileage
        job_report.heavy_mileage = \
            job_report.heavy_mileage + job.heavy_mileage
        job_report.highway_mileage = \
            job_report.highway_mileage + job.highway_mileage
        job_report.normalway_mileage = \
            job_report.normalway_mileage + job.normalway_mileage

        job_report.save()
    except m.JobReport.DoesNotExist:
        job_report = m.JobReport.objects.create(
            driver=driver,
            month=month.Month(job_year, job_month),
            total_mileage=job.total_mileage,
            empty_mileage=job.empty_mileage,
            heavy_mileage=job.heavy_mileage,
            highway_mileage=job.highway_mileage,
            normalway_mileage=job.normalway_mileage
        )
