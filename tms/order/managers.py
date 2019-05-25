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
