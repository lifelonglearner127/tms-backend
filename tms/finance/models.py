from django.db import models

from ..vehicle.models import Vehicle
from ..hr.models import Department
from ..order.models import Order


class BaseCard(models.Model):

    issue_company = models.CharField(
        max_length=100
    )

    number = models.CharField(
        max_length=100,
        unique=True
    )

    key = models.CharField(
        max_length=100
    )

    last_charge_date = models.DateField(
        null=True,
        blank=True
    )

    balance = models.PositiveIntegerField(
        default=0
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    class Meta:
        abstract = True
        ordering = ['-last_charge_date']


class ETCCard(BaseCard):

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE
    )


class FuelCard(BaseCard):

    master = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        related_name='children'
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True
    )


class OrderPayment(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=5,
        decimal_places=1
    )

    is_complete = models.BooleanField(
        default=False
    )
