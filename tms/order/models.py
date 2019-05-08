from django.db import models
from django.conf import settings

from ..core import constants
from ..core.models import TimeStampedModel
from ..info.models import LoadingStation, UnLoadingStation, Product


class Order(TimeStampedModel):
    """
    Order model
    """
    alias = models.CharField(
        max_length=100
    )

    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_order",
        null=True
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
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

    products = models.ManyToManyField(
        Product,
        through='OrderProduct'
    )


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
