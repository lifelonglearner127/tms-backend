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

    after_amount = models.FloatField(
        default=0
    )

    charged_on = models.DateField(
        null=True, blank=True
    )

    created_on = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = [
            '-charged_on', '-created_on'
        ]


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
        blank=True,
        related_name='children'
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    is_child = models.BooleanField(
        default=False
    )

    objects = models.Manager()
    masters = managers.FuelMasterCards()
    children = managers.FuelChildernCards()


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

    class Meta:
        ordering = ['-charged_on']


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


class Bill(CreatedTimeModel):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bills'
    )

    category = models.CharField(
        max_length=1,
        choices=c.BILL_CATEGORY,
        default=c.BILL_CATEGORY_MEAL
    )

    from_time = models.DateTimeField()

    to_time = models.DateTimeField()

    cost = models.FloatField(
        default=0
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    objects = models.Manager()
    meal_bills = managers.MealBillManager()
    parking_vehicle_bills = managers.ParkingVehicleBillManager()
    clean_vehicle_bills = managers.CleanVehicleBillManager()
    sleep_bills = managers.SleepBillManager()


class BillDocument(models.Model):

    bill = models.ForeignKey(
        Bill, on_delete=models.CASCADE, related_name='images'
    )

    document = models.ImageField()
