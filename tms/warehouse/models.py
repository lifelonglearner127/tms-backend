from django.db import models

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

    amount = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2
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

    unit_price = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2
    )

    amount = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2
    )

    price = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2
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

    unit_price = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2
    )

    price = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2
    )

    amount = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2
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
