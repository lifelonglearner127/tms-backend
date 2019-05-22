from django.db import models

from ..core import constants


class PendingOrderManager(models.Manager):
    """
    Pending Order Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            status=constants.ORDER_STATUS_PENDING
        )


class InProgressOrderManager(models.Manager):
    """
    In Progress Order Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            status=constants.ORDER_STATUS_INPROGRESS
        )


class CompleteOrderManager(models.Manager):
    """
    Complete Order Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            status=constants.ORDER_STATUS_COMPLETE
        )


class InternalOrderManager(models.Manager):
    """
    Internal Order Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            status=constants.ORDER_SOURCE_INTERNAL
        )


class CustomerOrderManager(models.Manager):
    """
    Customer Order Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            status=constants.ORDER_SOURCE_CUSTOMER
        )


class PendingJobManager(models.Manager):
    """
    Pending Job Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            status=constants.JOB_STATUS_PENDING
        )


class InProgressJobManager(models.Manager):
    """
    In Progress Job Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            status=constants.JOB_STATUS_INPROGRESS
        )


class CompleteJobManager(models.Manager):
    """
    Complete Job Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            status=constants.JOB_STATUS_COMPLETE
        )
