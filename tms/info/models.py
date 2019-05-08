from django.db import models

from ..core import constants
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
        choices=constants.PRODUCT_TYPE,
        default=constants.PRODUCT_TYPE_GASOLINE
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
    centroid = models.CharField(
        max_length=10,
        null=True,
        blank=True
    )

    radius = models.CharField(
        max_length=10,
        null=True,
        blank=True
    )

    price = models.DecimalField(
        max_digits=5,
        decimal_places=1,
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

    class Meta:
        abstract = True


class LoadStation(Station):
    """
    LoadStation model, used as base class
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        abstract = True


class LoadingStation(LoadStation):
    """
    LoadingStation model
    """
    def __str__(self):
        return self.name


class UnLoadingStation(LoadStation):
    """
    UnLoadingStation model
    """
    def __str__(self):
        return self.name


class QualityStation(Station):
    """
    QualityStation model
    """
    def __str__(self):
        return self.name


class OilStation(Station):
    """
    OilStation model
    """
    def __str__(self):
        return self.name
