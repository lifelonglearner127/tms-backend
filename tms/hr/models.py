from django.db import models
from datetime import datetime, timedelta
from math import ceil
import pytz

from . import managers
from ..core import constants as c
from ..core.models import TimeStampedModel
from ..account.models import User


class CompanySection(models.Model):

    text = models.CharField(
        max_length=100
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )


class Department(TimeStampedModel):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-updated', 'name']


class Position(TimeStampedModel):
    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-updated', 'name']


class RoleManagement(models.Model):

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )

    position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE
    )

    permission = models.PositiveIntegerField(
        choices=c.PERMISSION_TYPE,
        default=c.PERMISSION_TYPE_NO
    )

    class Meta:
        ordering = ['department', 'position']
        unique_together = ['department', 'position']


class DriverLicense(models.Model):

    name = models.CharField(
        max_length=100
    )

    number = models.CharField(
        max_length=100
    )

    expires_on = models.DateField()

    # document_type = models.CharField(
    #     max_length=1,
    #     choices=c.USER_DOCUMENT_TYPE,
    #     default=c.USER_DOCUMENT_TYPE_D1
    # )

    document_type = models.CharField(
        max_length=100
    )

    description = models.TextField(
        null=True,
        blank=True
    )


def days_hours_minutes(td):
    seconds = (td.seconds//60) % 60
    seconds += td.microseconds / 1e6
    return td.days, td.seconds//3600, seconds


def format_hms_string(time_diff):
    format_string = ""
    days, hours, mins = days_hours_minutes(time_diff)
    if days > 0:
        format_string += "{}天 ".format(days)
    if hours > 0:
        format_string += "{}小时 ".format(hours)
    if mins > 0:
        format_string += "{}分钟".format(ceil(mins))
    if mins == 0:
        format_string += "0分钟"
    return format_string


class StaffProfile(TimeStampedModel):
    """
    Staff Profile Model
    """
    user = models.OneToOneField(
        User,
        related_name='profile',
        on_delete=models.CASCADE
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )

    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True
    )

    id_card = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    birthday = models.DateField(
        null=True,
        blank=True
    )

    emergency_number = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    spouse_name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    spouse_number = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    parent_name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    parent_number = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    address = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    driver_license = models.ForeignKey(
        DriverLicense,
        on_delete=models.SET_NULL,
        null=True
    )

    status = models.CharField(
        max_length=1,
        choices=c.WORK_STATUS,
        default=c.WORK_STATUS_AVAILABLE
    )

    objects = models.Manager()
    availables = managers.AvailableStaffManager()
    notavailables = managers.NotAvailableStaffManager()
    drivers = managers.Drivers()
    escorts = managers.Escorts()
    inwork_drivers = managers.InWorkDrivers()
    available_drivers = managers.AvailableDrivers()
    inwork_escorts = managers.InWorkEscorts()
    available_escorts = managers.AvailableEscorts()
    wheels = managers.WheelUserManager()

    def __str__(self):
        return '{}-{}\'s profile'.format(
            self.user.user_type, self.user.username
        )

    @property
    def driving_duration(self):
        bind = self.user.my_vehicle_bind.first()

        if bind is not None and bind.get_off is None:
            dt1 = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
            time_duration = dt1 - bind.get_on
        elif bind is not None and bind.get_off is not None:
            time_duration = bind.get_off - bind.get_on
        else:
            time_duration = timedelta(0)

        result = format_hms_string(time_duration)
        return result

    # @property
    # def next_job_customer(self):
    #     next_job = self.user.jobs_as_driver.filter(progress=1).first()
    #     customer_name = ''
    #     if next_job:
    #         next_order = next_job.order.first()
    #         if next_order:
    #             customer = next_order.customer.first()
    #             customer_name = customer.user.username
    #     return customer_name


class CustomerContact(models.Model):

    contact = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    mobile = models.CharField(
        max_length=30,
        null=True,
        blank=True
    )


class CustomerProfile(TimeStampedModel):
    """
    Customer Profile Model
    """
    name = models.CharField(
        max_length=100
    )

    address = models.CharField(
        max_length=500,
        null=True,
        blank=True
    )

    user = models.OneToOneField(
        User,
        related_name='customer_profile',
        on_delete=models.CASCADE
    )

    associated_with = models.ForeignKey(
        User,
        related_name='incharges_customers',
        on_delete=models.SET_NULL,
        null=True
    )

    customer_request = models.TextField(
        null=True,
        blank=True
    )

    contacts = models.ManyToManyField(
        CustomerContact
    )

    class Meta:
        ordering = ['-updated']
