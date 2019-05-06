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

    price = models.DecimalField(
        max_digits=5,
        decimal_places=1
    )

    description = models.TextField()


class Station(BasicContactModel):

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

    class Meta:
        abstract = True


class LoadStation(Station):

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True
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
