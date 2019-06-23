from django.db import models

from . import managers
from ..core import constants as c
from ..core.models import TimeStampedModel, BasicContactModel


class Product(TimeStampedModel):
    """
    Product model
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )

    code = models.CharField(
        max_length=100,
        unique=True
    )

    category = models.CharField(
        max_length=10,
        choices=c.PRODUCT_CATEGORY,
        default=c.PRODUCT_CATEGORY_GASOLINE
    )

    price = models.DecimalField(
        max_digits=c.PRICE_MAX_DIGITS,
        decimal_places=c.PRICE_DECIMAL_PLACES
    )

    unit_weight = models.PositiveIntegerField(
        default=1
    )

    weight_measure_unit = models.CharField(
        max_length=1,
        choices=c.PRODUCT_WEIGHT_MEASURE_UNIT,
        default=c.PRODUCT_WEIGHT_MEASURE_UNIT_TON
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-updated']

    def __str__(self):
        return self.name


class Station(BasicContactModel):
    """
    Station model, used as base class
    """
    station_type = models.CharField(
        max_length=1,
        choices=c.STATION_TYPE,
    )

    longitude = models.FloatField()

    latitude = models.FloatField()

    radius = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    product_category = models.CharField(
        max_length=10,
        choices=c.PRODUCT_CATEGORY,
        default=c.PRODUCT_CATEGORY_GASOLINE
    )

    price = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True
    )

    working_time = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    working_time_measure_unit = models.CharField(
        max_length=1,
        choices=c.TIME_MEASURE_UNIT,
        default=c.TIME_MEASURE_UNIT_HOUR
    )

    average_time = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    average_time_measure_unit = models.CharField(
        max_length=1,
        choices=c.TIME_MEASURE_UNIT,
        default=c.TIME_MEASURE_UNIT_HOUR
    )

    price_vary_duration = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    price_vary_duration_unit = models.CharField(
        max_length=1,
        choices=c.PRICE_VARY_DURATION_UNIT,
        default=c.PRICE_VARY_DURATION_UNIT_MONTH
    )

    notification_message = models.TextField(
        null=True,
        blank=True
    )

    objects = models.Manager()
    loadingstations = managers.LoadingStationManager()
    unloadingstations = managers.UnLoadingStationManager()
    qualitystations = managers.QualityStationManager()
    workstations = managers.WorkStationManager()
    oilstations = managers.OilStationManager()
    blackdots = managers.BlackDotManager()

    class Meta:
        unique_together = ('longitude', 'latitude')
        ordering = ['-updated']
