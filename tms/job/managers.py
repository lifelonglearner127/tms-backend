from django.db import models

from ..core import constants as c


class PendingJobManager(models.Manager):
    """
    Pending Job Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            status=c.JOB_STATUS_PENDING
        )


class InProgressJobManager(models.Manager):
    """
    In Progress Job Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            status=c.JOB_STATUS_INPROGRESS
        )


class CompleteJobManager(models.Manager):
    """
    Complete Job Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            status=c.JOB_STATUS_COMPLETE
        )
