from django.db import models

from ..core import constants as c
from ..core.models import ApprovedModel
from ..account.models import User
from ..vehicle.models import Vehicle
from ..order.models import Job


class ParkingRequest(ApprovedModel):

    job = models.ForeignKey(
        Job,
        on_delete=models.SET_NULL,
        null=True
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='parking_requests'
    )

    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='parking_requests_as_driver'
    )

    escort = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='parking_requests_as_escort'
    )

    place = models.CharField(
        max_length=100
    )


class DriverChangeRequest(ApprovedModel):

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE
    )

    old_driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='driver_change_requests'
    )

    new_driver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='driver_change_assigned'
    )

    change_time = models.DateTimeField(
        null=True,
        blank=True
    )

    change_place = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['approved', '-approved_time', '-request_time']
        unique_together = ['job', 'old_driver']


class EscortChangeRequest(ApprovedModel):

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE
    )

    old_escort = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='escort_change_requests'
    )

    new_escort = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='escort_change_assigned'
    )

    change_time = models.DateTimeField(
        null=True,
        blank=True
    )

    change_place = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['approved', '-approved_time', '-request_time']
        unique_together = ['job', 'old_escort']


class RestRequest(ApprovedModel):

    user = models.ForeignKey(
        User,
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
        unique_together = ['user', 'from_date', 'to_date']
