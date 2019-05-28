from django.db import models

from . import managers
from ..core import constants as c
from ..core.models import TimeStampedModel, BasicContactModel


class Product(TimeStampedModel):
    """
    Product model
    """
    name = models.CharField(
        max_length=100
    )

    code = models.CharField(
        max_length=100
    )

    category = models.CharField(
        max_length=10,
        choices=c.PRODUCT_TYPE,
        default=c.PRODUCT_TYPE_GASOLINE
    )

    price = models.DecimalField(
        max_digits=5,
        decimal_places=1
    )

    description = models.TextField()

    def __str__(self):
        return self.name


class Station(BasicContactModel):
    """
    Station model, used as base class
    """
    station_type = models.CharField(
        max_length=1,
        choices=c.STATION_TYPE,
        default=c.STATION_TYPE_LOADING_STATION
    )

    longitude = models.FloatField()

    latitude = models.FloatField()

    radius = models.DecimalField(
        max_digits=10,
        decimal_places=1
    )

    product_category = models.CharField(
        max_length=10,
        choices=c.PRODUCT_TYPE,
        default=c.PRODUCT_TYPE_GASOLINE
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True
    )

    working_time = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True
    )

    average_time = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True
    )

    objects = models.Manager()
    loading = managers.LoadingStationManager()
    unloading = managers.UnLoadingStationManager()
    quality = managers.QualityStationManager()
    oil = managers.OilStationManager()

    class Meta:
        unique_together = (
            'longitude', 'latitude'
        )
