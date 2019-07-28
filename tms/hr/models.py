from django.db import models

from . import managers
from ..core import constants as c
from ..core.models import BasicContactModel, TimeStampedModel
from ..account.models import User


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
    inwork_drivers = managers.InWorkDrivers()
    available_drivers = managers.AvailableDrivers()
    inwork_escorts = managers.InWorkEscorts()
    available_escorts = managers.AvailableEscorts()

    def __str__(self):
        return '{}-{}\'s profile'.format(
            self.user.role, self.user.username
        )


class CustomerProfile(BasicContactModel):
    """
    Customer Profile Model
    """
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

    class Meta:
        ordering = ['-updated']
