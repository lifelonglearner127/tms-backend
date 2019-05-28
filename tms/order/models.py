from django.db import models

from . import managers
from ..core import constants as c
from ..core.models import TimeStampedModel
from ..info.models import Station, Product
from ..account.models import StaffProfile, CustomerProfile


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

    order_source = models.CharField(
        max_length=1,
        choices=c.ORDER_SOURCE,
        default=c.ORDER_SOURCE_INTERNAL
    )

    status = models.CharField(
        max_length=1,
        choices=c.ORDER_STATUS,
        default=c.ORDER_STATUS_PENDING
    )

    loading_stations = models.ManyToManyField(
        Station,
        through='OrderLoadingStation',
        through_fields=('order', 'loading_station')
    )

    objects = models.Manager()
    pendings = managers.PendingOrderManager()
    inprogress = managers.InProgressOrderManager()
    completeds = managers.CompleteOrderManager()
    from_internal = managers.InternalOrderManager()
    from_customer = managers.CustomerOrderManager()

    def __str__(self):
        return self.alias


class OrderLoadingStation(models.Model):
    """
    Intermediate model for order model and loading station
    Currently order has only one loading station, but I create it
    for future business logic
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )

    loading_station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name='loading_stations'
    )

    quality_station = models.ForeignKey(
        Station,
        on_delete=models.SET_NULL,
        related_name='unloading_stations',
        null=True,
        blank=True
    )

    products = models.ManyToManyField(
        Product,
        through='OrderProduct'
    )

    due_time = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return '{} - Load from {} at {}'.format(
            self.order.alias, self.loading_station.name, self.due_time
        )


class OrderProduct(models.Model):
    """
    Intermediate model for order model and product model
    """
    order_loading_station = models.ForeignKey(
        OrderLoadingStation,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    total_weight = models.PositiveIntegerField()

    weight_unit = models.CharField(
        max_length=2,
        choices=c.UNIT_WEIGHT,
        default=c.UNIT_WEIGHT_TON
    )

    loss = models.PositiveIntegerField(
        default=0
    )

    loss_unit = models.CharField(
        max_length=2,
        choices=c.UNIT_WEIGHT,
        default=c.UNIT_WEIGHT_TON
    )

    payment_unit = models.CharField(
        max_length=2,
        choices=c.UNIT_WEIGHT,
        default=c.UNIT_WEIGHT_TON
    )

    is_split = models.BooleanField(
        default=False
    )

    is_pump = models.BooleanField(
        default=False
    )

    unloading_stations = models.ManyToManyField(
        Station,
        through='OrderProductDeliver'
    )

    def __str__(self):
        return 'Order from {}- {} of {}'.format(
            self.order_loading_station.loading_station,
            self.total_weight, self.product.name
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
        Station,
        on_delete=models.CASCADE
    )

    weight = models.PositiveIntegerField()

    def __str__(self):
        return 'Order {}: from {} to {}: {} of {}'.format(
            self.order_product.order_loading_station.order,
            self.order_product.order_loading_station.loading_station.name,
            self.unloading_station.name,
            self.weight, self.order_product.total_weight
        )
