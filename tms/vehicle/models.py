from django.db import models
from django.contrib.postgres.fields import ArrayField

from . import managers
from ..core import constants as c
from ..core.models import TimeStampedModel


class Vehicle(TimeStampedModel):
    """
    Vehicle model
    """
    model = models.CharField(
        max_length=1,
        choices=c.VEHICLE_MODEL_TYPE,
        default=c.VEHICLE_MODEL_TYPE_TRUCK
    )

    plate_num = models.CharField(
        max_length=100,
        unique=True
    )

    code = models.CharField(
        max_length=100
    )

    brand = models.CharField(
        max_length=1,
        choices=c.VEHICLE_BRAND,
        default=c.VEHICLE_BRAND_TONGHUA
    )

    load = models.DecimalField(
        max_digits=5,
        decimal_places=1
    )

    branches = ArrayField(
        models.PositiveIntegerField()
    )

    status = models.CharField(
        max_length=1,
        choices=c.VEHICLE_STATUS,
        default=c.VEHICLE_STATUS_AVAILABLE
    )

    longitude = models.FloatField(
        null=True,
        blank=True
    )

    latitude = models.FloatField(
        null=True,
        blank=True
    )

    speed = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    @property
    def branch_count(self):
        return len(self.branches)

    objects = models.Manager()
    inworks = managers.InWorkVehicleManager()
    availables = managers.AvailableVehicleManager()
    repairs = managers.RepairVehicleManager()

    def __str__(self):
        return self.plate_num


class VehicleDocument(models.Model):
    """
    Vehicle Document model
    """
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE
    )

    code = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    document_type = models.CharField(
        max_length=1,
        choices=c.VEHICLE_DOCUMENT_TYPE,
        default=c.VEHICLE_DOCUMENT_TYPE_D1
    )

    authority = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    registered_on = models.DateField()

    expires_on = models.DateField()

    def __str__(self):
        return '{}\'s {} document'.format(self.vehicle.no, self.code)
