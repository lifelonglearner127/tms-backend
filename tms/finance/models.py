from django.db import models

from . import managers
from ..core import constants as c
from ..core.models import CreatedTimeModel
from ..account.models import User
from ..hr.models import Department
from ..order.models import Order
from ..vehicle.models import Vehicle


class BaseCard(models.Model):

    issue_company = models.CharField(
        max_length=100
    )

    issued_on = models.DateField(
        null=True,
        blank=True
    )

    number = models.CharField(
        max_length=100
    )

    key = models.CharField(
        max_length=100
    )

    last_charge_date = models.DateField(
        null=True,
        blank=True
    )

    balance = models.FloatField(
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


class ETCCardChargeHistory(models.Model):

    card = models.ForeignKey(
        ETCCard,
        on_delete=models.CASCADE
    )

    previous_amount = models.FloatField(
        default=0
    )

    charged_amount = models.FloatField(
        default=0
    )

    charged_on = models.DateField(
        auto_now_add=True
    )


class ETCCardUsageHistory(models.Model):

    card = models.ForeignKey(
        ETCCard,
        on_delete=models.CASCADE
    )

    amount = models.FloatField(
        default=0
    )

    address = models.CharField(
        max_length=200
    )

    paid_on = models.DateTimeField()


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


class FuelCardChargeHistory(models.Model):

    card = models.ForeignKey(
        FuelCard,
        on_delete=models.CASCADE
    )

    previous_amount = models.FloatField(
        default=0
    )

    charged_amount = models.FloatField(
        default=0
    )

    charged_on = models.DateTimeField()


class FuelCardUsageHistory(models.Model):

    card = models.ForeignKey(
        ETCCard,
        on_delete=models.CASCADE
    )

    amount = models.FloatField(
        default=0
    )

    address = models.CharField(
        max_length=200
    )

    paid_on = models.DateTimeField()


class OrderPayment(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=c.WEIGHT_MAX_DIGITS,
        decimal_places=c.WEIGHT_DECIMAL_PLACES
    )

    is_complete = models.BooleanField(
        default=False
    )


class BillDocument(CreatedTimeModel):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bills'
    )

    # job = models.ForeignKey(
    #     Job,
    #     on_delete=models.SET_NULL,
    #     related_name='bills',
    #     null=True
    # )

    amount = models.DecimalField(
        max_digits=c.WEIGHT_MAX_DIGITS,
        decimal_places=c.WEIGHT_DECIMAL_PLACES,
        null=True,
        blank=True
    )

    unit_price = models.DecimalField(
        max_digits=c.PRICE_MAX_DIGITS,
        decimal_places=c.PRICE_DECIMAL_PLACES,
        null=True,
        blank=True
    )

    cost = models.DecimalField(
        max_digits=c.PRICE_MAX_DIGITS,
        decimal_places=c.PRICE_DECIMAL_PLACES,
        null=True,
        blank=True
    )

    bill = models.ImageField()

    category = models.PositiveIntegerField(
        choices=c.BILL_CATEGORY
    )

    sub_category = models.PositiveIntegerField(
        default=0
    )

    detail_category = models.PositiveIntegerField(
        default=0
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    objects = models.Manager()
    stationbills = managers.StationBillDocumentManager()
    otherbills = managers.OtherBillDocumentManager()

    def __str__(self):
        return '{} bill from {}'.format(
            self.get_category_display(),
            self.user
        )

    class Meta:
        ordering = [
            'category'
        ]
