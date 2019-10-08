from django.db import models

from . import managers
from ..core import constants as c
from ..core.models import TimeStampedModel, BasicContactModel
from ..hr.models import CustomerProfile


class Product(TimeStampedModel):
    """
    Product model
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )

    level = models.PositiveIntegerField(
        default=3
    )

    # code = models.CharField(
    #     max_length=100,
    #     unique=True
    # )

    # category = models.ForeignKey(
    #     ProductCategory,
    #     on_delete=models.CASCADE
    # )

    # price = models.FloatField(
    #     default=0
    # )

    # unit_weight = models.PositiveIntegerField(
    #     default=1
    # )

    # weight_measure_unit = models.CharField(
    #     max_length=1,
    #     choices=c.PRODUCT_WEIGHT_MEASURE_UNIT,
    #     default=c.PRODUCT_WEIGHT_MEASURE_UNIT_TON
    # )

    description = models.TextField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-updated']

    def __str__(self):
        return self.name


class BasicSetting(TimeStampedModel):

    tax_rate = models.FloatField(
        default=0
    )

    rapid_acceleration = models.PositiveIntegerField(
        default=0
    )

    rapid_deceleration = models.PositiveIntegerField(
        default=0
    )

    sharp_turn = models.PositiveIntegerField(
        default=0
    )

    over_speed = models.PositiveIntegerField(
        default=0
    )

    over_speed_duration = models.PositiveIntegerField(
        default=0
    )

    rotation_speed = models.PositiveIntegerField(
        default=0
    )

    vehicle_review_duration = models.PositiveIntegerField(
        default=0
    )

    driver_license_duration = models.PositiveIntegerField(
        default=0
    )

    vehicle_operation_duration = models.PositiveIntegerField(
        default=0
    )

    vehicle_insurance_duration = models.PositiveIntegerField(
        default=0
    )


class Station(BasicContactModel):
    """
    Station model, used as base class
    """
    station_type = models.CharField(
        max_length=1,
        choices=c.STATION_TYPE,
    )

    longitude = models.FloatField(
        default=0
    )

    latitude = models.FloatField(
        default=0
    )

    radius = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    products = models.ManyToManyField(
        Product
    )

    customers = models.ManyToManyField(
        CustomerProfile
    )

    price = models.FloatField(
        default=0
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

    description = models.TextField(
        null=True,
        blank=True
    )

    objects = models.Manager()
    loadingstations = managers.LoadingStationManager()
    unloadingstations = managers.UnLoadingStationManager()
    qualitystations = managers.QualityStationManager()
    loadingqualitystations = managers.LoadingQualityStationManager()
    workstations = managers.WorkStationManager()
    oilstations = managers.OilStationManager()
    blackdots = managers.BlackDotManager()
    parkingstations = managers.ParkingStationManager()
    getoffstations = managers.GetoffStationManager()

    class Meta:
        ordering = ['station_type', '-updated']

    def __str__(self):
        return self.name


class TransportationDistance(TimeStampedModel):

    name = models.CharField(
        max_length=100
    )

    start_point = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name='start_points'
    )

    end_point = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name='end_points'
    )

    distance = models.FloatField(
        default=0
    )

    average_time = models.FloatField(
        default=1
    )

    description = models.TextField(
        null=True,
        blank=True
    )


class OtherCostType(models.Model):

    name = models.CharField(
        max_length=100
    )


class TicketType(models.Model):

    name = models.CharField(
        max_length=100
    )
