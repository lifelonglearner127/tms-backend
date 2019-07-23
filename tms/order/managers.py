from django.db import models

from ..core import constants as c


class PendingOrderManager(models.Manager):
    """
    Pending Order Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            status=c.ORDER_STATUS_PENDING
        )


class InProgressOrderManager(models.Manager):
    """
    In Progress Order Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            status=c.ORDER_STATUS_INPROGRESS
        )


class CompleteOrderManager(models.Manager):
    """
    Complete Order Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            status=c.ORDER_STATUS_COMPLETE
        )


class InternalOrderManager(models.Manager):
    """
    Internal Order Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            status=c.ORDER_SOURCE_INTERNAL
        )


class CustomerOrderManager(models.Manager):
    """
    Customer Order Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            status=c.ORDER_SOURCE_CUSTOMER
        )


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


class AdminVehicleUserBindManager(models.Manager):
    """
    Manager for getting in repairing vehicles
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            bind_method=c.VEHICLE_USER_BIND_METHOD_BY_ADMIN
        )


class JobVehicleUserBindManager(models.Manager):
    """
    Manager for getting in repairing vehicles
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            bind_method=c.VEHICLE_USER_BIND_METHOD_BY_JOB
        )
