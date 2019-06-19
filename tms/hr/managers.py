from django.db import models

from ..core import constants as c


class AvailableStaffManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            status=c.WORK_STATUS_AVAILABLE
        )


class NotAvailableStaffManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            status=c.WORK_STATUS_NOT_AVAILABLE
        )
