from django.db import models

from ..core import constants as c


class MealBillManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            category=c.BILL_CATEGORY_MEAL
        )


class ParkingVehicleBillManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            category=c.BILL_CATEGORY_PARKING_VEHICLE
        )


class CleanVehicleBillManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            category=c.BILL_CATEGORY_CLEAN_VEHICLE
        )


class SleepBillManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            category=c.BILL_CATEGORY_SLEEP
        )


class MasterCards(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_child=False)


class ChildernCards(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_child=True)
