from django.db import models

from ..core import constants
from ..core.models import CreatedTimeModel
from ..vehicle.models import Vehicle
from ..account.models import User
from ..order.models import OrderProductDeliver


class PendingJobManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            status=constants.JOB_STATUS_PENDING
        )


class InProgressJobManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            status=constants.JOB_STATUS_INPROGRESS
        )


class CompleteJobManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            status=constants.JOB_STATUS_COMPLETE
        )


class Job(CreatedTimeModel):

    mission = models.ForeignKey(
        OrderProductDeliver,
        on_delete=models.CASCADE
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    driver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='jobs_as_primary',
        null=True,
        blank=True
    )

    escort = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='jobs_as_escort',
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=1,
        choices=constants.JOB_STATUS,
        default=constants.JOB_STATUS_PENDING
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True
    )

    finished_at = models.DateTimeField(
        null=True,
        blank=True
    )

    objects = models.Manager()
    pendings = PendingJobManager()
    inprogress = InProgressJobManager()
    completeds = CompleteJobManager()
