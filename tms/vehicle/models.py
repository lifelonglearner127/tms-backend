from django.db import models
from django.db.models import Q

from ..core import constants
from ..core.models import TimeStampedModel


class InProgressVehicle(models.Manager):
    """
    Manager for retrieving in progress vehicles
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            jobs__status=constants.JOB_STATUS_INPROGRESS
        )


class AvailableVehicle(models.Manager):
    """
    Manager for retrieving available vehicles
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            ~Q(jobs__status=constants.JOB_STATUS_INPROGRESS)
        )


class Vehicle(TimeStampedModel):
    """
    Vehicle model
    """
    model = models.CharField(
        max_length=1,
        choices=constants.VEHICLE_MODEL_TYPE,
        default=constants.VEHICLE_MODEL_TYPE_TRUCK
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
        choices=constants.VEHICLE_BRAND,
        default=constants.VEHICLE_BRAND_TONGHUA
    )

    load = models.DecimalField(
        max_digits=5,
        decimal_places=1
    )

    objects = models.Manager()
    inprogress = InProgressVehicle()
    availables = AvailableVehicle()

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
