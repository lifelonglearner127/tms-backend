"""
todo: code optimization, sending notification logic was used in multiple places
"""
import datetime
import json
import month
from django.shortcuts import get_object_or_404
from config.celery import app
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from ..core import constants as c
from ..core.aliyunpush import aliyun_client, aliyun_request
from ..core.redis import r

# models
from . import models as m
from ..account.models import User
from ..notification.models import Notification
from ..vehicle.models import Vehicle

# serializers
from ..notification.serializers import NotificationSerializer


channel_layer = get_channel_layer()


@app.task
def notify_order_changes(context):
    order = get_object_or_404(m.Order, id=context['order'])
    customer = get_object_or_404(User, id=context['customer_user_id'])
    message = {
        "created": order.created.strftime('%Y-%m-%d'),
        "products": []
    }

    for order_product in order.orderproduct_set.all():
        message['products'].append({
            'product': order_product.product.name,
            'weight': order_product.weight
        })
    customer_notification = Notification.objects.create(
        user=customer,
        msg_type=c.CUSTOMER_NOTIFICATION_NEW_ORDER,
        message=message
    )

    if customer.channel_name:
        async_to_sync(channel_layer.send)(
            customer.channel_name,
            {
                'type': 'notify',
                'data': json.dumps(
                    NotificationSerializer(customer_notification).data
                )
            }
        )

    # send push notification to customer
    if customer.device_token:
        aliyun_request.set_Title('Cancel Job')
        aliyun_request.set_Body('Cancel Job')
        aliyun_request.set_TargetValue(customer.device_token)
        aliyun_client.do_action(aliyun_request)


@app.task
def notify_of_job_creation(context):
    """
    When the job is created, notification is sent to the driver and escort
    and customer will be notified as well
    """
    job = get_object_or_404(m.Job, id=context['job'])
    driver = get_object_or_404(User, id=context['driver'])
    escort = get_object_or_404(User, id=context['escort'])

    # send in-app notfication to driver
    stations = []
    for job_station in job.jobstation_set.all():
        products = []
        for jobstationproduct in job_station.jobstationproduct_set.all():
            product = jobstationproduct.product.name + '(' +\
                      str(jobstationproduct.mission_weight) + ')'
            products.append(product)

        stations.append({
            'station': job_station.station.address,
            'products': ', '.join(products)
        })

    message = {
        "vehicle": job.vehicle.plate_num,
        "customer": {
            "name": job.order.customer.name,
            "mobile": job.order.customer.mobile
        },
        "driver": {
            "name": driver.name,
            "mobile": driver.mobile
        },
        "escort": {
            "name": escort.name,
            "mobile": escort.mobile
        },
        "stations": stations
    }

    driver_notification = Notification.objects.create(
        user=job.driver,
        message=message,
        msg_type=c.DRIVER_NOTIFICATION_NEW_JOB
    )

    escort_notification = Notification.objects.create(
        user=job.escort,
        message=message,
        msg_type=c.DRIVER_NOTIFICATION_NEW_JOB
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

    message = {
        "vehicle": job.vehicle.plate_num,
        "driver": {
            "name": job.driver.name,
            "mobile": job.driver.mobile
        },
        "escort": {
            "name": job.escort.name,
            "mobile": job.escort.mobile
        }
    }
    message['stations'] = stations

    customer_notification = Notification.objects.create(
        user=job.order.customer.user,
        message=message,
        msg_type=c.CUSTOMER_NOTIFICATION_NEW_ARRANGEMENT
    )

    if job.order.customer.user.channel_name:
        async_to_sync(channel_layer.send)(
            job.order.customer.user.channel_name,
            {
                'type': 'notify',
                'data': json.dumps(
                    NotificationSerializer(customer_notification).data
                )
            }
        )

    # TODO: now push notification api is called twice; one for driver and other for escort
    # This would be not effeciency and there might be a solution to send bulk notification using one api call

    # send push notification to driver
    if job.driver.device_token:
        aliyun_request.set_Title('New Job')
        aliyun_request.set_Body('New Job')
        aliyun_request.set_TargetValue(job.driver.device_token)
        aliyun_client.do_action(aliyun_request)

    # send push notification to escort
    if job.escort.device_token:
        aliyun_request.set_Title('New Job')
        aliyun_request.set_Body('New Job')
        aliyun_request.set_TargetValue(job.escort.device_token)
        aliyun_client.do_action(aliyun_request)

    if job.order.customer.user.device_token:
        aliyun_request.set_Title('New Job')
        aliyun_request.set_Body('New Job')
        aliyun_request.set_TargetValue(job.escort.device_token)
        aliyun_client.do_action(aliyun_request)


@app.task
def notify_of_driver_changes_before_job_start(context):
    """
    when the job driver changes before the job start,
    1. old driver will be notified
    2. new driver will be notified about
    """
    pass


@app.task
def notify_of_escort_changes_before_job_start(context):
    """
    """
    pass


@app.task
def notify_of_job_products_changes(context):
    """
    """
    pass


@app.task
def notify_of_job_deleted(context):
    """
    send notification when the job is deleted
    """
    job_id = context['job']
    vehicle = get_object_or_404(Vehicle, id=context['vehicle'])
    driver = get_object_or_404(User, id=context['driver'])
    escort = get_object_or_404(User, id=context['escort'])

    r.srem('jobs', job_id)

    # send notification
    message = {
        "vehicle": vehicle.plate_num,
        "notification": str(job_id) + ' was cancelled'
    }

    driver_notification = Notification.objects.create(
        user=driver,
        message=message,
        msg_type=c.DRIVER_NOTIFICATION_DELETE_JOB
    )

    escort_notification = Notification.objects.create(
        user=escort,
        message=message,
        msg_type=c.DRIVER_NOTIFICATION_DELETE_JOB
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
            escort.channel_name,
            {
                'type': 'notify',
                'data': json.dumps(
                    NotificationSerializer(escort_notification).data
                )
            }
        )

    # send push notification to driver
    if driver.device_token:
        aliyun_request.set_Title('Cancel Job')
        aliyun_request.set_Body('Cancel Job')
        aliyun_request.set_TargetValue(driver.device_token)
        aliyun_client.do_action(aliyun_request)

    # send push notification to escort
    if escort.device_token:
        aliyun_request.set_Title('Cancel Job')
        aliyun_request.set_Body('Cancel Job')
        aliyun_request.set_TargetValue(escort.device_token)
        aliyun_client.do_action(aliyun_request)


@app.task
def calculate_job_report(context):
    job = get_object_or_404(m.Job, id=context['job'])
    vehicle = get_object_or_404(Vehicle, id=context['vehicle'])
    driver = get_object_or_404(User, id=context['driver'])
    escort = get_object_or_404(User, id=context['escort'])

    if not job.order.jobs.filter(
        progress__gt=c.JOB_PROGRESS_COMPLETE
    ).exists():
        job.order.status = c.ORDER_STATUS_COMPLETE
        job.order.save()

        order_year = job.order.created.year
        order_month = job.order.created.month

        try:
            order_report = m.OrderReport.objects.get(
                customer=job.order.customer,
                month=month.Month(order_year, order_month)
            )
            order_report.orders += 1
            order_report.weight += job.order.total_weight
            order_report.save()
        except m.OrderReport.DoesNotExist:
            m.OrderReport.objects.create(
                customer=job.order.customer,
                month=month.Month(order_year, order_month),
                orders=1,
                weights=job.order.total_weight
            )

    # # unbind vehicle, driver, escort
    # if not m.VehicleUserBind.binds_by_admin.filter(
    #     vehicle=vehicle,
    #     driver=driver,
    #     escort=escort
    # ).exists():
    #     try:
    #         vehicle_bind = m.VehicleUserBind.objects.get(
    #             vehicle=vehicle,
    #             driver=driver,
    #             escort=escort,
    #             bind_method=c.VEHICLE_USER_BIND_METHOD_BY_JOB
    #         )
    #         vehicle_bind.delete()
    #     except m.VehicleUserBind.DoesNotExist:
    #         pass

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


@app.task
def bind_vehicle_user(context):
    job = get_object_or_404(m.Job, id=context['job'])

    # # bind vehicle, driver, escort
    # if not m.VehicleUserBind.binds_by_admin.filter(
    #     vehicle=job.vehicle,
    #     driver=job.driver,
    #     escort=job.escort
    # ).exists():
    #     m.VehicleUserBind.objects.get_or_create(
    #         vehicle=job.vehicle,
    #         driver=job.driver,
    #         escort=job.escort,
    #         bind_method=c.VEHICLE_USER_BIND_METHOD_BY_JOB
    #     )

    # set the vehicle status to in-work
    job.vehicle.status = c.VEHICLE_STATUS_INWORK
    job.vehicle.save()

    # set the driver & escrot to in-work
    job.driver.profile.status = c.WORK_STATUS_DRIVING
    job.escort.profile.status = c.WORK_STATUS_DRIVING
    job.driver.profile.save()
    job.escort.profile.save()




@app.task
def update_monthly_report():
    time = datetime.datetime.now()
    for user in User.objects.all():
        if user.user_type in [c.USER_TYPE_DRIVER, c.USER_TYPE_ESCORT]:
            if not m.JobReport.objects.filter(driver=user, month=month.Month(time.year, time.month)).exists():
                m.JobReport.objects.create(driver=user, month=month.Month(time.year, time.month))

        elif user.user_type == c.USER_TYPE_CUSTOMER:
            if not m.OrderReport.objects.filter(
                customer=user.customer_profile, month=month.Month(time.year, time.month)
            ).exists():
                m.OrderReport.objects.create(customer=user.customer_profile, month=month.Month(time.year, time.month))
