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
from .utils import get_branches
from ..account.models import User
from ..notification.models import Notification
# from ..vehicle.models import Vehicle

# serializers
from ..notification.serializers import NotificationSerializer


channel_layer = get_channel_layer()


def send_notifications(users, message, message_type):

    for user in users:
        notification = Notification.objects.create(
            user=user,
            message=message,
            msg_type=message_type
        )

        if user.channel_name:
            async_to_sync(channel_layer.send)(
                user.channel_name,
                {
                    'type': 'notify',
                    'data': json.dumps(
                        NotificationSerializer(notification).data
                    )
                }
            )

        # send push notification to driver
        if user.device_token:
            aliyun_request.set_Title(message_type)
            aliyun_request.set_Body(message_type)
            aliyun_request.set_TargetValue(user.device_token)
            aliyun_client.do_action(aliyun_request)


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

    send_notifications([customer], message, c.CUSTOMER_NOTIFICATION_NEW_ORDER)


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
    message = {
        "vehicle": job.vehicle.plate_num,
        "customer": {
            "name": job.order.customer.contacts.first().contact,
            "mobile": job.order.customer.contacts.first().mobile
        },
        "driver": {
            "name": driver.name,
            "mobile": driver.mobile
        },
        "escort": {
            "name": escort.name,
            "mobile": escort.mobile
        },
        "loading_station": job.order.loading_station.address,
        "branches": get_branches(job),
        "rest_place": job.rest_place.address if job.rest_place is not None else '-'
    }

    send_notifications([driver, escort], message, c.DRIVER_NOTIFICATION_NEW_JOB)

    message = {
        "vehicle": job.vehicle.plate_num,
        "driver": {
            "name": driver.name,
            "mobile": driver.mobile
        },
        "escort": {
            "name": escort.name,
            "mobile": escort.mobile
        }
    }

    send_notifications([job.order.customer.user], message, c.CUSTOMER_NOTIFICATION_NEW_ARRANGEMENT)


@app.task
def notify_of_driver_or_escort_changes_before_job_start(context):
    """
    when the job driver changes before the job start,
     - if only driver changes, new driver will be notified, old driver will be notified, escort will be notified
     - if only escort changes, new escort will be notified, old escort will be notified, drivier will be notified
    """
    job = get_object_or_404(m.Job, id=context['job'])
    current_driver = get_object_or_404(User, id=context['current_driver'])
    current_escort = get_object_or_404(User, id=context['current_escort'])
    new_driver = get_object_or_404(User, id=context['new_driver'])
    new_escort = get_object_or_404(User, id=context['new_escort'])
    is_driver_updated = context['is_driver_updated']
    is_escort_updated = context['is_escort_updated']

    new_job_message = {
        "vehicle": job.vehicle.plate_num,
        "customer": {
            "name": job.order.customer.contacts.first().contact,
            "mobile": job.order.customer.contacts.first().mobile
        },
        "driver": {
            "name": new_driver.name,
            "mobile": new_driver.mobile
        },
        "escort": {
            "name": new_escort.name,
            "mobile": new_escort.mobile
        },
        "loading_station": job.order.loading_station.address,
        "branches": get_branches(job),
        "rest_place": job.rest_place.address if job.rest_place is not None else '-'
    }

    cancel_job_message = {
        "vehicle": job.vehicle.plate_num,
        "customer": {
            "name": job.order.customer.contacts.first().contact,
            "mobile": job.order.customer.contacts.first().mobile
        },
        "driver": {
            "name": current_driver.name,
            "mobile": current_driver.mobile
        },
        "escort": {
            "name": current_escort.name,
            "mobile": current_escort.mobile
        },
        "loading_station": job.order.loading_station.address,
        "branches": get_branches(job),
        "rest_place": job.rest_place.address if job.rest_place is not None else '-'
    }

    change_message = new_job_message

    if is_driver_updated and is_escort_updated:
        send_notifications([current_driver, current_escort], cancel_job_message, c.DRIVER_NOTIFICATION_CANCEL_JOB)
        send_notifications([new_driver, new_escort], new_job_message, c.DRIVER_NOTIFICATION_NEW_JOB)

    elif is_driver_updated and not is_escort_updated:
        send_notifications([current_driver], cancel_job_message, c.DRIVER_NOTIFICATION_CANCEL_JOB)
        send_notifications([new_driver], new_job_message, c.DRIVER_NOTIFICATION_NEW_JOB)
        # change_message = {
        #     "driver": {
        #         "name": new_driver.name,
        #         "mobile": new_driver.mobile
        #     }
        # }
        send_notifications([current_escort], change_message, c.DRIVER_NOTIFICATION_UPDATE_JOB)
    elif not is_driver_updated and is_escort_updated:
        send_notifications([current_escort], cancel_job_message, c.DRIVER_NOTIFICATION_CANCEL_JOB)
        send_notifications([new_escort], new_job_message, c.DRIVER_NOTIFICATION_NEW_JOB)
        # change_message = {
        #     "escort": {
        #         "name": new_escort.name,
        #         "mobile": new_escort.mobile
        #     }
        # }
        send_notifications([current_driver], change_message, c.DRIVER_NOTIFICATION_UPDATE_JOB)


@app.task
def notify_of_job_products_changes(context):
    """
    """
    job = get_object_or_404(m.Job, id=context['job'])
    driver = get_object_or_404(User, id=context['driver'])
    escort = get_object_or_404(User, id=context['escort'])

    message = {
        "vehicle": job.vehicle.plate_num,
        "customer": {
            "name": job.order.customer.contacts.first().contact,
            "mobile": job.order.customer.contacts.first().mobile
        },
        "driver": {
            "name": driver.name,
            "mobile": driver.mobile
        },
        "escort": {
            "name": escort.name,
            "mobile": escort.mobile
        },
        "loading_station": job.order.loading_station.address,
        "branches": get_branches(job),
        "rest_place": job.rest_place.address
    }

    send_notifications([driver, escort], message, c.DRIVER_NOTIFICATION_UPDATE_JOB)

    send_notifications([job.order.customer.user], message, c.CUSTOMER_NOTIFICATION_UPDATE_ARRANGEMENT)


@app.task
def notify_of_job_deleted(context):
    """
    send notification when the job is deleted
    """
    job_id = context['job']
    vehicle = context['vehicle']
    driver = get_object_or_404(User, id=context['driver'])
    escort = get_object_or_404(User, id=context['escort'])

    r.srem('jobs', job_id)

    # send notification
    # message = {
    #     "vehicle": vehicle,
    #     "notification": str(job_id) + ' was cancelled'
    # }
    message = {
        "vehicle": vehicle,
        "customer": {
            "name": context['customer_name'],
            "mobile": context['customer_mobile']
        },
        "driver": {
            "name": driver.name,
            "mobile": driver.mobile
        },
        "escort": {
            "name": escort.name,
            "mobile": escort.mobile
        },
        "loading_station": context['loading_station'],
        "branches": context['branches'],
        "rest_place": context['rest_place']
    }

    send_notifications([driver, escort], message, c.DRIVER_NOTIFICATION_DELETE_JOB)


@app.task
def calculate_job_report(context):
    job = get_object_or_404(m.Job, id=context['job'])
    # vehicle = get_object_or_404(Vehicle, id=context['vehicle'])
    driver = get_object_or_404(User, id=context['driver'])
    # escort = get_object_or_404(User, id=context['escort'])

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
