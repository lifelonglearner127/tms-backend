from django.db import models

from ..core import constants as c


class PendingJobManager(models.Manager):
    """
    Pending Job Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            progress=c.JOB_PROGRESS_NOT_STARTED
        )


class InProgressJobManager(models.Manager):
    """
    In Progress Job Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            progress__gt=c.JOB_PROGRESS_NOT_STARTED
        )


class CompleteJobManager(models.Manager):
    """
    Complete Job Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            progress=c.JOB_PROGRESS_COMPLETE
        )
