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
def notify_job_changes(context):
    """
    Send notificatio when a new job is created
    """
    job = get_object_or_404(m.Job, id=context['job'])

    # bind vehicle, driver, escort
    if not VehicleUserBind.binds_by_admin.filter(
        vehicle=job.vehicle,
        driver=job.driver,
        escort=job.escort
    ).exists():
        VehicleUserBind.objects.get_or_create(
            vehicle=job.vehicle,
            driver=job.driver,
            escort=job.escort,
            bind_method=c.VEHICLE_USER_BIND_METHOD_BY_JOB
        )

    # set the vehicle status to in-work
    job.vehicle.status = c.VEHICLE_STATUS_INWORK
    job.vehicle.save()

    # set the driver & escrot to in-work
    job.driver.profile.status = c.WORK_STATUS_DRIVING
    job.escort.profile.status = c.WORK_STATUS_DRIVING
    job.driver.profile.save()
    job.escort.profile.save()

    # send in-app notfication to driver & escort
    message = {
        "vehicle": job.vehicle.plate_num,
        "customer":
        job.order.customer.name + ' (' + job.order.customer.mobile + ')',
        "escort": job.escort.name + ' (' + job.escort.mobile + ')',
        "loading": job.loading_station.address,
        "quality": job.quality_station.address,
        "unloadings": []
    }
    for mission in job.mission_set.all():
        message['unloadings'].append({
            'station': mission.mission.unloading_station.address,
            'product': mission.mission.order_product.product.name + ' (' +
            str(mission.mission_weight) + ')'
        })

    driver_notification = Notification.objects.create(
        user=job.driver,
        message=message,
        msg_type=c.DRIVER_NOTIFICATION_TYPE_JOB
    )

    escort_notification = Notification.objects.create(
        user=job.escort,
        message=message,
        msg_type=c.DRIVER_NOTIFICATION_TYPE_JOB
    )

    if job.driver.channel_name:
        async_to_sync(channel_layer.send)(
            job.driver.channel_name,
            {
                'type': 'notify',
                'data': json.dumps(
                    NotificationSerializer(driver_notification).data
                )
            }
        )

    if job.escort.channel_name:
        async_to_sync(channel_layer.send)(
            job.escort.channel_name,
            {
                'type': 'notify',
                'data': json.dumps(
                    NotificationSerializer(escort_notification).data
                )
            }
        )

    # send push notification to driver & escort
    if job.driver.device_token:
        to = [job.driver.device_token]
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
    job = get_object_or_404(m.Job, id=context['job'])
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
