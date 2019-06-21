from django.db import models

from . import managers
from ..core import constants as c
from ..core.models import ApprovedModel, BasicContactModel
from ..account.models import User
from ..info.models import Product


class Department(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['name']


class Position(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['name']


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

    document_type = models.CharField(
        max_length=1,
        choices=c.USER_DOCUMENT_TYPE,
        default=c.USER_DOCUMENT_TYPE_D1
    )

    description = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )


class StaffProfile(models.Model):
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

    products = models.ManyToManyField(
        Product
    )

    product_characteristics = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    payment_method = models.CharField(
        max_length=1,
        choices=c.PAYMENT_METHOD,
        default=c.PAYMENT_METHOD_TON
    )

    associated_with = models.ForeignKey(
        StaffProfile,
        related_name='customers',
        on_delete=models.SET_NULL,
        null=True
    )

    customer_request = models.TextField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-updated']


class RestRequest(ApprovedModel):

    staff = models.ForeignKey(
        StaffProfile,
        on_delete=models.CASCADE
    )

    category = models.PositiveIntegerField(
        choices=c.REST_REQUEST_CATEGORY,
        default=c.REST_REQUEST_ILL
    )

    from_date = models.DateField()

    to_date = models.DateField()

    class Meta:
        ordering = ['approved', '-approved_time', '-request_time']
        unique_together = ['staff', 'from_date', 'to_date']
