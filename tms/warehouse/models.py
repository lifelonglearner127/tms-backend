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
        max_length=100
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
        max_length=100
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

    ticket_type = models.CharField(
        max_length=100,
        null=True,
        blank=True
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

    vehicle = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    unit_price = models.FloatField(
        default=0
    )

    price = models.FloatField(
        default=0
    )

    amount = models.FloatField(
        default=0
    )

    amount_unit = models.CharField(
        max_length=100
    )

    ticket_type = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    transaction_on = models.DateTimeField()
