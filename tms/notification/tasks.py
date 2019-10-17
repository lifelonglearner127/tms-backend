from datetime import date
from config.celery import app
from ..core import constants as c
from . import models as m
from ..info.models import BasicSetting


@app.task
def remind_expires_events():
    basic_setting = BasicSetting.objects.first()

    vehicle_review_duration = 2
    driver_license_duration = 2
    vehicle_operation_duration = 2
    vehicle_insurance_duration = 2

    if basic_setting is not None:
        if basic_setting.vehicle_review_duration > 0:
            vehicle_review_duration = basic_setting.vehicle_review_duration

        if basic_setting.driver_license_duration > 0:
            driver_license_duration = basic_setting.driver_license_duration

        if basic_setting.vehicle_operation_duration > 0:
            vehicle_operation_duration = basic_setting.vehicle_operation_duration

        if basic_setting.vehicle_insurance_duration > 0:
            vehicle_insurance_duration = basic_setting.vehicle_insurance_duration

    # check if driver license expires
    today = date.today()
    for user in m.User.wheels.all():
        if user.profile.driver_license is None:
            continue

        if (user.profile.driver_license.expires_on - today).days < driver_license_duration:
            m.Event.objects.get_or_create(
                event_type=c.EVENT_TYPE_DRIVER_LICENSE_EXPIRED,
                expires_on=user.profile.driver_license.expires_on,
                driver=user
            )

    for vehicle in m.Vehicle.objects.all():
        if vehicle.insurance_expires_on is not None:
            if (vehicle.insurance_expires_on - today).days < vehicle_insurance_duration:
                m.Event.objects.get_or_create(
                    event_type=c.EVENT_TYPE_VEHICLE_INSURANCE_EXPIRED,
                    is_head=True,
                    expires_on=vehicle.insurance_expires_on,
                    vehicle=vehicle
                )

        if vehicle.insurance_expires_on_2 is not None:
            if (vehicle.insurance_expires_on_2 - today).days < vehicle_insurance_duration:
                m.Event.objects.get_or_create(
                    event_type=c.EVENT_TYPE_VEHICLE_INSURANCE_EXPIRED,
                    is_head=False,
                    expires_on=vehicle.insurance_expires_on_2,
                    vehicle=vehicle
                )
