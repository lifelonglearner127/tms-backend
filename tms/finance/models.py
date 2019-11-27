from django.db import models

from . import managers
from ..core import constants as c
from ..core.models import CreatedTimeModel
from ..account.models import User
from ..hr.models import Department
from ..vehicle.models import Vehicle
from ..info.models import Station


class BaseCard(models.Model):

    master = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    vehicle = models.OneToOneField(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    is_child = models.BooleanField(
        default=False
    )

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

    balance = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    objects = models.Manager()
    masters = managers.MasterCards()
    children = managers.ChildernCards()

    class Meta:
        abstract = True
        ordering = ['-last_charge_date']


class ETCCard(BaseCard):
    pass


class ETCCardChargeHistory(models.Model):

    card = models.ForeignKey(
        ETCCard,
        on_delete=models.CASCADE
    )

    previous_amount = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2
    )

    charged_amount = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2
    )

    after_amount = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2
    )

    charged_on = models.DateTimeField(
        null=True, blank=True
    )

    created_on = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = [
            '-charged_on', '-created_on'
        ]


class ETCBillHistory(models.Model):

    card = models.ForeignKey(
        ETCCard,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    is_card = models.BooleanField(
        default=False
    )

    driver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    amount = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2
    )

    address = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )

    description = models.TextField(
        null=True, blank=True
    )

    paid_on = models.DateTimeField(
        null=True, blank=True
    )

    created_on = models.DateTimeField(
        auto_now_add=True
    )

    objects = models.Manager()
    cash_history = managers.CashHistoryManager()
    card_history = managers.CardHistoryManager()

    class Meta:
        ordering = [
            '-paid_on', '-created_on',
        ]


class ETCBillDocument(models.Model):

    etc_bill = models.ForeignKey(
        ETCBillHistory,
        on_delete=models.CASCADE,
        related_name='images'
    )

    document = models.ImageField()


class FuelCard(BaseCard):
    pass


class FuelCardChargeHistory(models.Model):

    card = models.ForeignKey(
        FuelCard,
        on_delete=models.CASCADE
    )

    previous_amount = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2
    )

    charged_amount = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2
    )

    after_amount = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2
    )

    charged_on = models.DateTimeField(
        null=True, blank=True
    )

    created_on = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-charged_on', '-created_on']


class FuelBillHistory(models.Model):

    card = models.ForeignKey(
        FuelCard,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    is_card = models.BooleanField(
        default=False
    )

    driver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    oil_station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE
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

    total_price = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2
    )

    address = models.CharField(
        max_length=200
    )

    description = models.TextField(
        null=True, blank=True
    )

    paid_on = models.DateTimeField(
        null=True, blank=True
    )

    created_on = models.DateTimeField(
        auto_now_add=True
    )

    objects = models.Manager()
    cash_history = managers.CashHistoryManager()
    card_history = managers.CardHistoryManager()

    class Meta:
        ordering = [
            '-paid_on', '-created_on',
        ]


class FuelBillDocument(models.Model):

    fuel_bill = models.ForeignKey(
        FuelBillHistory,
        on_delete=models.CASCADE,
        related_name='images'
    )

    document = models.ImageField()


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

    cost = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2
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
