from django.db import models

from ..core import constants as c

# models
from ..account.models import User
from ..core.models import TimeStampedModel


class WarehouseProduct(TimeStampedModel):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    assignee = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    amount = models.FloatField(
        default=0
    )

    amount_unit = models.CharField(
        max_length=1,
        choices=c.WEIGHT_UNIT
    )


class InTransaction(TimeStampedModel):

    product = models.ForeignKey(
        WarehouseProduct,
        on_delete=models.CASCADE,
        related_name='in_transactions'
    )

    unit_price = models.FloatField(
        default=0
    )

    amount = models.FloatField(
        default=0
    )

    price = models.FloatField(
        default=0
    )

    amount_unit = models.CharField(
        max_length=1,
        choices=c.WEIGHT_UNIT
    )

    supplier = models.CharField(
        max_length=100
    )

    supplier_contact = models.CharField(
        max_length=100
    )

    supplier_mobile = models.CharField(
        max_length=100
    )

    transaction_on = models.DateTimeField()


class OutTransaction(TimeStampedModel):

    product = models.ForeignKey(
        WarehouseProduct,
        on_delete=models.CASCADE,
        related_name='out_transactions'
    )

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    amount = models.FloatField(
        default=0
    )

    amount_unit = models.CharField(
        max_length=1,
        choices=c.WEIGHT_UNIT
    )

    transaction_on = models.DateTimeField()
