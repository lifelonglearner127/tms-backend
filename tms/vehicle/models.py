from django.db import models

from ..core import constants
from ..core.models import TimeStampedModel


class Vehicle(TimeStampedModel):
    """
    Vehicle model
    """
    model = models.CharField(
        max_length=1,
        choices=constants.VEHICLE_MODEL_TYPE,
        default=constants.VEHICLE_MODEL_TYPE_TRUCK
    )

    no = models.CharField(
        max_length=100
    )

    code = models.CharField(
        max_length=100
    )

    brand = models.CharField(
        max_length=1,
        choices=constants.VEHICLE_BRAND,
        default=constants.VEHICLE_BRAND_TONGHUA
    )

    load = models.DecimalField(
        max_digits=5,
        decimal_places=1
    )

    def __str__(self):
        return self.no


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
        choices=constants.VEHICLE_DOCUMENT_TYPE,
        default=constants.VEHICLE_DOCUMENT_TYPE_D1
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
