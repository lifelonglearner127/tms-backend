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


class InWorkDrivers(models.Manager):
    """
    Manager for getting in-work drivers
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            user__role=c.USER_ROLE_DRIVER,
            status=c.WORK_STATUS_DRIVING
        )


class AvailableDrivers(models.Manager):
    """
    Manager for getting available drivers
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            user__role=c.USER_ROLE_DRIVER,
            status=c.WORK_STATUS_AVAILABLE
        )


class InWorkEscorts(models.Manager):
    """
    Manager for getting in-work escorts
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            user__role=c.USER_ROLE_ESCORT,
            status=c.WORK_STATUS_DRIVING
        )


class AvailableEscorts(models.Manager):
    """
    Manager for getting available escorts
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            user__role=c.USER_ROLE_ESCORT,
            status=c.WORK_STATUS_AVAILABLE
        )
