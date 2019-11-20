from datetime import date
from config.celery import app
from ..core import constants as c
from . import models as m
from ..info.models import BasicSetting


@app.task
def remind_expires_events():
    bs = BasicSetting.objects.first()

    if bs is None:
        return

    if bs.driver_license_expires_notification_duration > 0:
        if bs.driver_license_expires_notification_duration_unit == c.DOCUMENT_EXPIRES_NOTIFICATION_DURATION_DAY:
            dr_ls_expires_nf_duration = bs.driver_license_expires_notification_duration
        elif bs.driver_license_expires_notification_duration_unit == c.DOCUMENT_EXPIRES_NOTIFICATION_DURATION_MONTH:
            dr_ls_expires_nf_duration = bs.driver_license_expires_notification_duration * 30

    else:
        dr_ls_expires_nf_duration = 10

    if bs.driver_work_license_expires_notification_duration > 0:
        if bs.driver_work_license_expires_notification_duration_unit == c.DOCUMENT_EXPIRES_NOTIFICATION_DURATION_DAY:
            dr_work_ls_expires_nf_duration = bs.driver_work_license_expires_notification_duration
        elif bs.driver_work_license_expires_notification_duration_unit ==\
                c.DOCUMENT_EXPIRES_NOTIFICATION_DURATION_MONTH:
            dr_work_ls_expires_nf_duration = bs.driver_work_license_expires_notification_duration * 30

    else:
        dr_ls_expires_nf_duration = 10

    if bs.vehicle_license_expires_notification_duration > 0:
        if bs.vehicle_license_expires_notification_duration_unit == c.DOCUMENT_EXPIRES_NOTIFICATION_DURATION_DAY:
            vh_ls_expires_nf_duration = bs.vehicle_license_expires_notification_duration
        elif bs.vehicle_license_expires_notification_duration_unit == c.DOCUMENT_EXPIRES_NOTIFICATION_DURATION_MONTH:
            vh_ls_expires_nf_duration = bs.vehicle_license_expires_notification_duration * 30
    else:
        vh_ls_expires_nf_duration = 10

    if bs.vehicle_operation_permit_notification_duration > 0:
        if bs.vehicle_operation_permit_notification_duration_unit == c.DOCUMENT_EXPIRES_NOTIFICATION_DURATION_DAY:
            vh_op_permit_nf_duration = bs.vehicle_operation_permit_notification_duration
        elif bs.vehicle_operation_permit_notification_duration_unit == c.DOCUMENT_EXPIRES_NOTIFICATION_DURATION_MONTH:
            vh_op_permit_nf_duration = bs.vehicle_operation_permit_notification_duration * 30
    else:
        vh_op_permit_nf_duration = 10

    if bs.vehicle_insurance_notification_duration > 0:
        if bs.vehicle_insurance_notification_duration_unit == c.DOCUMENT_EXPIRES_NOTIFICATION_DURATION_DAY:
            vh_is_nf_duration = bs.vehicle_insurance_notification_duration
        elif bs.vehicle_insurance_notification_duration_unit == c.DOCUMENT_EXPIRES_NOTIFICATION_DURATION_MONTH:
            vh_is_nf_duration = bs.vehicle_insurance_notification_duration * 30
    else:
        vh_is_nf_duration = 10

    # check if driver license expires
    today = date.today()
    for user in m.User.wheels.all():
        if user.profile.driver_license is None:
            continue

        if (user.profile.driver_license.expires_on - today).days < dr_ls_expires_nf_duration:
            m.Event.objects.get_or_create(
                event_type=c.EVENT_TYPE_DRIVER_LICENSE_EXPIRED,
                expires_on=user.profile.driver_license.expires_on,
                driver=user
            )

        if (user.profile.driver_license.work_license_expires_on - today).days < dr_work_ls_expires_nf_duration:
            m.Event.objects.get_or_create(
                event_type=c.EVENT_TYPE_DRIVER_LICENSE_EXPIRED,
                expires_on=user.profile.driver_license.work_license_expires_on,
                driver=user
            )

    # check if vehicle documents expires
    for vehicle in m.Vehicle.objects.all():
        # check if head vehicle license expires
        if vehicle.license_expires_on is not None:
            if (vehicle.license_expires_on - today).days < vh_ls_expires_nf_duration:
                m.Event.objects.get_or_create(
                    event_type=c.EVENT_TYPE_VEHICLE_LICENSE_EXPIRED,
                    is_head=True,
                    expires_on=vehicle.insurance_expires_on,
                    vehicle=vehicle
                )

        # check if second vehicle license expires
        if vehicle.license_expires_on_2 is not None:
            if (vehicle.license_expires_on_2 - today).days < vh_ls_expires_nf_duration:
                m.Event.objects.get_or_create(
                    event_type=c.EVENT_TYPE_VEHICLE_LICENSE_EXPIRED,
                    is_head=False,
                    expires_on=vehicle.license_expires_on_2,
                    vehicle=vehicle
                )

        # check if head vehicle operation permit document expires
        if vehicle.operation_permit_expires_on is not None:
            if (vehicle.operation_permit_expires_on - today).days < vh_op_permit_nf_duration:
                m.Event.objects.get_or_create(
                    event_type=c.EVENT_TYPE_VEHICLE_OPERATION_PERMIT_EXPIRED,
                    is_head=True,
                    expires_on=vehicle.insurance_expires_on,
                    vehicle=vehicle
                )

        # check if second vehicle operation permit document expires
        if vehicle.operation_permit_expires_on_2 is not None:
            if (vehicle.operation_permit_expires_on_2 - today).days < vh_op_permit_nf_duration:
                m.Event.objects.get_or_create(
                    event_type=c.EVENT_TYPE_VEHICLE_OPERATION_PERMIT_EXPIRED,
                    is_head=False,
                    expires_on=vehicle.operation_permit_expires_on_2,
                    vehicle=vehicle
                )

        # check if head vehicle insurance document expires
        if vehicle.insurance_expires_on is not None:
            if (vehicle.insurance_expires_on - today).days < vh_is_nf_duration:
                m.Event.objects.get_or_create(
                    event_type=c.EVENT_TYPE_VEHICLE_INSURANCE_EXPIRED,
                    is_head=True,
                    expires_on=vehicle.insurance_expires_on,
                    vehicle=vehicle
                )

        # check if second vehicle insurance document expires
        if vehicle.insurance_expires_on_2 is not None:
            if (vehicle.insurance_expires_on_2 - today).days < vh_is_nf_duration:
                m.Event.objects.get_or_create(
                    event_type=c.EVENT_TYPE_VEHICLE_INSURANCE_EXPIRED,
                    is_head=False,
                    expires_on=vehicle.insurance_expires_on_2,
                    vehicle=vehicle
                )
