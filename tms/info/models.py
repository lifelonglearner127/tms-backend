from django.db import models

from ..core import constants
from ..core.models import TimeStampedModel, BasicContactModel


class Product(TimeStampedModel):

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

    unit_price = models.DecimalField(
        max_digits=5,
        decimal_places=1
    )

    description = models.TextField()


class Station(BasicContactModel):

    efence_centroid = models.CharField(
        max_length=10,
        null=True,
        blank=True
    )

    efence_radius = models.CharField(
        max_length=10,
        null=True,
        blank=True
    )

    unit_price = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True
    )

    unit_time = models.PositiveSmallIntegerField(
        null=True,
        blank=True
    )

    duration_unit = models.CharField(
        max_length=10,
        choices=constants.DURATION_UNIT,
        default=constants.DURATION_UNIT_HOUR
    )

    class Meta:
        abstract = True


class LoadStation(Station):

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True
    )

    average_time = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        null=True,
        blank=True
    )

    class Meta:
        abstract = True


class LoadingStation(LoadStation):
    pass


class UnLoadingStation(LoadStation):
    pass


class QualityStation(Station):
    pass


class OilStation(Station):
    pass
