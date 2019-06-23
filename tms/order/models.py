from django.db import models

from . import managers
from ..core import constants as c
from ..core.models import TimeStampedModel
from ..info.models import Station, Product
from ..account.models import User


class Order(TimeStampedModel):
    """
    Order model
    """
    alias = models.CharField(
        max_length=100
    )

    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='charge_orders',
        null=True
    )

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
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

    @property
    def products(self):
        products = []
        for order_loading_station in self.orderloadingstation_set.all():
            products.extend(order_loading_station.products.all())

        return products

    objects = models.Manager()
    pendings = managers.PendingOrderManager()
    inprogress = managers.InProgressOrderManager()
    completeds = managers.CompleteOrderManager()
    from_internal = managers.InternalOrderManager()
    from_customer = managers.CustomerOrderManager()

    def __str__(self):
        return self.alias

    class Meta:
        ordering = ['-updated']


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

    due_time = models.DateTimeField()

    products = models.ManyToManyField(
        Product,
        through='OrderProduct'
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

    total_weight = models.DecimalField(
        max_digits=c.WEIGHT_MAX_DIGITS,
        decimal_places=c.WEIGHT_DECIMAL_PLACES,
    )

    total_weight_measure_unit = models.CharField(
        max_length=1,
        choices=c.PRODUCT_WEIGHT_MEASURE_UNIT,
        default=c.PRODUCT_WEIGHT_MEASURE_UNIT_TON
    )

    price = models.DecimalField(
        max_digits=c.PRICE_MAX_DIGITS,
        decimal_places=c.PRICE_DECIMAL_PLACES,
        default=0
    )

    price_weight_measure_unit = models.CharField(
        max_length=1,
        choices=c.PRODUCT_WEIGHT_MEASURE_UNIT,
        default=c.PRODUCT_WEIGHT_MEASURE_UNIT_TON
    )

    loss = models.DecimalField(
        max_digits=c.WEIGHT_MAX_DIGITS,
        decimal_places=c.WEIGHT_DECIMAL_PLACES,
        default=0
    )

    loss_unit = models.CharField(
        max_length=2,
        choices=c.PRODUCT_WEIGHT_MEASURE_UNIT,
        default=c.PRODUCT_WEIGHT_MEASURE_UNIT_TON
    )

    payment_method = models.CharField(
        max_length=1,
        choices=c.PAYMENT_METHOD,
        default=c.PAYMENT_METHOD_TON
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

    due_time = models.DateTimeField()

    weight = models.PositiveIntegerField()

    def __str__(self):
        return 'Order {}: from {} to {}: {} of {}'.format(
            self.order_product.order_loading_station.order,
            self.order_product.order_loading_station.loading_station.name,
            self.unloading_station.name,
            self.weight, self.order_product.total_weight
        )
