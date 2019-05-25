from django.db import models
from django.contrib.postgres.fields import ArrayField

from . import managers
from ..core import constants as c
from ..account.models import DriverProfile, EscortProfile
from ..vehicle.models import Vehicle
from ..order.models import OrderProductDeliver
from ..road.models import Route


class Job(models.Model):
    """
    Job model
    """
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE
    )

    driver = models.ForeignKey(
        DriverProfile,
        on_delete=models.CASCADE,
        related_name='jobs'
    )

    escort = models.ForeignKey(
        EscortProfile,
        on_delete=models.CASCADE,
        related_name='jobs',
    )

    route = models.ForeignKey(
        Route,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    progress = models.CharField(
        max_length=2,
        choices=c.JOB_STATUS,
        default=c.JOB_STATUS_NOT_STARTED
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True
    )

    arrived_time = ArrayField(
        models.DateTimeField(),
        null=True,
        blank=True
    )

    departure_time = ArrayField(
        models.DateTimeField(),
        null=True,
        blank=True
    )

    finished_at = models.DateTimeField(
        null=True,
        blank=True
    )

    missions = models.ManyToManyField(
        OrderProductDeliver,
        through='Mission'
    )

    total_weight = models.PositiveIntegerField()

    objects = models.Manager()
    pendings = managers.PendingJobManager()
    inprogress = managers.InProgressJobManager()
    completeds = managers.CompleteJobManager()


class Mission(models.Model):

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE
    )

    mission = models.ForeignKey(
        OrderProductDeliver,
        on_delete=models.CASCADE
    )

    mission_weight = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    loading_weight = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    unloading_weight = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    is_completed = models.BooleanField(
        default=False
    )
