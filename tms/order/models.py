from django.db import models

from ..core import constants
from ..core.models import TimeStampedModel, CreatedTimeModel
from ..info.models import LoadingStation, UnLoadingStation, Product
from ..vehicle.models import Vehicle
from ..account.models import StaffProfile, CustomerProfile


class PendingOrderManager():
    """
    Pending Order Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            status=constants.ORDER_STATUS_PENDING
        )


class InProgressOrderManager():
    """
    In Progress Order Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            status=constants.ORDER_STATUS_INPROGRESS
        )


class CompleteOrderManager():
    """
    Complete Order Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            status=constants.ORDER_STATUS_COMPLETE
        )


class InternalOrderManager():
    """
    Internal Order Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            status=constants.ORDER_SOURCE_INTERNAL
        )


class CustomerOrderManager():
    """
    Customer Order Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            status=constants.ORDER_SOURCE_CUSTOMER
        )


class Order(TimeStampedModel):
    """
    Order model
    """
    alias = models.CharField(
        max_length=100
    )

    assignee = models.ForeignKey(
        StaffProfile,
        on_delete=models.SET_NULL,
        null=True
    )

    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
    )

    loading_station = models.ForeignKey(
        LoadingStation,
        on_delete=models.SET_NULL,
        null=True
    )

    rest_place = models.CharField(
        max_length=100
    )

    change_place = models.CharField(
        max_length=100
    )

    source = models.CharField(
        max_length=1,
        choices=constants.ORDER_SOURCE,
        default=constants.ORDER_SOURCE_INTERNAL
    )

    status = models.CharField(
        max_length=1,
        choices=constants.ORDER_STATUS,
        default=constants.ORDER_STATUS_PENDING
    )

    products = models.ManyToManyField(
        Product,
        through='OrderProduct'
    )

    objects = models.Manager()
    pendings = PendingOrderManager()
    inprogress = InProgressOrderManager()
    completeds = CompleteOrderManager()
    from_internal = InternalOrderManager()
    from_customer = CustomerOrderManager()

    def __str__(self):
        return self.alias


class OrderProduct(models.Model):
    """
    Intermediate model for order model and product model
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True
    )

    total_weight = models.PositiveIntegerField()

    weight_unit = models.CharField(
        max_length=2,
        choices=constants.UNIT_WEIGHT,
        default=constants.UNIT_WEIGHT_TON
    )

    loss = models.PositiveIntegerField(
        default=0
    )

    loss_unit = models.CharField(
        max_length=2,
        choices=constants.UNIT_WEIGHT,
        default=constants.UNIT_WEIGHT_TON
    )

    payment_unit = models.CharField(
        max_length=2,
        choices=constants.UNIT_WEIGHT,
        default=constants.UNIT_WEIGHT_TON
    )

    is_split = models.BooleanField(
        default=False
    )

    is_pump = models.BooleanField(
        default=False
    )

    unloading_stations = models.ManyToManyField(
        UnLoadingStation,
        through='OrderProductDeliver'
    )

    def __str__(self):
        return '{}-{}: {}{}'.format(
            self.order.alias, self.product.name,
            self.total_weight, self.weight_unit
        )


class OrderProductDeliver(models.Model):
    """
    Intermediate model for ordered product and unloading station
    """
    order_product = models.ForeignKey(
        OrderProduct,
        on_delete=models.CASCADE
    )

    unloading_station = models.ForeignKey(
        UnLoadingStation,
        on_delete=models.SET_NULL,
        null=True
    )

    weight = models.PositiveIntegerField()

    def __str__(self):
        return '{} in {}-{} to {}'.format(
            self.weight, self.order_product.order.alias,
            self.order_product.product.name, self.unloading_station.name
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


class Job(CreatedTimeModel):
    """
    Job model
    """
    mission = models.ForeignKey(
        OrderProductDeliver,
        on_delete=models.CASCADE,
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        related_name='jobs',
        null=True,
        blank=True
    )

    driver = models.ForeignKey(
        StaffProfile,
        on_delete=models.SET_NULL,
        related_name='jobs_as_primary',
        null=True,
        blank=True
    )

    escort = models.ForeignKey(
        StaffProfile,
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
