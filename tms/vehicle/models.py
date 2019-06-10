from django.db import models
from django.contrib.postgres.fields import ArrayField

from . import managers
from ..core import constants as c
from ..core.models import TimeStampedModel


class Vehicle(TimeStampedModel):
    """
    Vehicle model
    """
    # Basic Information
    model = models.CharField(
        max_length=1,
        choices=c.VEHICLE_MODEL_TYPE,
        default=c.VEHICLE_MODEL_TYPE_TRUCK
    )

    plate_num = models.CharField(
        max_length=100,
        unique=True
    )

    identifier_code = models.CharField(
        max_length=100
    )

    brand = models.CharField(
        max_length=1,
        choices=c.VEHICLE_BRAND,
        default=c.VEHICLE_BRAND_TONGHUA
    )

    use_for = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    total_load = models.DecimalField(
        max_digits=5,
        decimal_places=1
    )

    actual_load = models.DecimalField(
        max_digits=5,
        decimal_places=1
    )

    affiliation_unit = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    use_started_on = models.DateField(
        null=True,
        blank=True
    )

    use_expires_on = models.DateField(
        null=True,
        blank=True
    )

    service_area = models.CharField(
        max_length=100
    )

    obtain_method = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    attribute = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    # Identity Information
    cert_type = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    cert_id = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    cert_authority = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    cert_registered_on = models.DateField(
        null=True,
        blank=True
    )

    cert_active_on = models.DateField(
        null=True,
        blank=True
    )

    cert_expires_on = models.DateField(
        null=True,
        blank=True
    )

    insurance_active_on = models.DateField(
        null=True,
        blank=True
    )

    insurance_expires_on = models.DateField(
        null=True,
        blank=True
    )

    # Position Information
    branches = ArrayField(
        models.PositiveIntegerField()
    )

    # Hardware Information
    engine_model = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    engine_power = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    transmission_model = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    engine_displacement = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    tire_rules = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    tank_material = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    is_gps_installed = models.BooleanField(
        default=False
    )

    is_gps_working = models.BooleanField(
        default=False
    )

    with_pump = models.BooleanField(
        default=False
    )

    main_car_size = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    main_car_color = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    trailer_car_size = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    trailer_car_color = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=1,
        choices=c.VEHICLE_STATUS,
        default=c.VEHICLE_STATUS_AVAILABLE
    )

    longitude = models.FloatField(
        null=True,
        blank=True
    )

    latitude = models.FloatField(
        null=True,
        blank=True
    )

    speed = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    @property
    def branch_count(self):
        return len(self.branches)

    objects = models.Manager()
    inworks = managers.InWorkVehicleManager()
    availables = managers.AvailableVehicleManager()
    repairs = managers.RepairVehicleManager()

    class Meta:
        ordering = ['-updated']

    def __str__(self):
        return self.plate_num
