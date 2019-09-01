from django.db import models
from django.contrib.postgres.fields import ArrayField

from . import managers
from ..core import constants as c

# models
from ..core.models import TimeStampedModel
from ..account.models import User
from ..info.models import Station


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
        max_digits=c.WEIGHT_MAX_DIGITS,
        decimal_places=c.WEIGHT_DECIMAL_PLACES
    )

    actual_load = models.DecimalField(
        max_digits=c.WEIGHT_MAX_DIGITS,
        decimal_places=c.WEIGHT_DECIMAL_PLACES
    )

    model_2 = models.CharField(
        max_length=1,
        choices=c.VEHICLE_MODEL_TYPE,
        default=c.VEHICLE_MODEL_TYPE_TRUCK
    )

    plate_num_2 = models.CharField(
        max_length=100,
        unique=True
    )

    identifier_code_2 = models.CharField(
        max_length=100
    )

    brand_2 = models.CharField(
        max_length=1,
        choices=c.VEHICLE_BRAND,
        default=c.VEHICLE_BRAND_TONGHUA
    )

    use_for_2 = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    total_load_2 = models.DecimalField(
        max_digits=c.WEIGHT_MAX_DIGITS,
        decimal_places=c.WEIGHT_DECIMAL_PLACES
    )

    actual_load_2 = models.DecimalField(
        max_digits=c.WEIGHT_MAX_DIGITS,
        decimal_places=c.WEIGHT_DECIMAL_PLACES
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
        max_length=100,
        null=True,
        blank=True
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

    cert_type_2 = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    cert_id_2 = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    cert_authority_2 = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    cert_registered_on_2 = models.DateField(
        null=True,
        blank=True
    )

    cert_active_on_2 = models.DateField(
        null=True,
        blank=True
    )

    cert_expires_on_2 = models.DateField(
        null=True,
        blank=True
    )

    insurance_active_on_2 = models.DateField(
        null=True,
        blank=True
    )

    insurance_expires_on_2 = models.DateField(
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


class Tire(TimeStampedModel):

    model = models.CharField(
        max_length=100
    )

    tire_type = models.CharField(
        max_length=100
    )

    tread_depth = models.FloatField(
        default=0
    )

    mileage_limit = models.PositiveIntegerField(
        default=0
    )

    use_cycle = models.PositiveIntegerField(
        default=0
    )


class FuelConsumption(TimeStampedModel):

    vehicle_type = models.CharField(
        max_length=100
    )

    high_way = models.FloatField(
        default=0
    )

    normal_way = models.FloatField(
        default=0
    )

    description = models.TextField(
        null=True,
        blank=True
    )


class VehicleMaintenanceHistory(TimeStampedModel):

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE
    )

    category = models.PositiveIntegerField(
        choices=c.VEHICLE_MAINTENANCE_CATEGORY,
        default=c.VEHICLE_MAINTENANCE_CATEGORY_WHEEL
    )

    maintenance_date = models.DateField()

    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    station = models.ForeignKey(
        Station,
        on_delete=models.SET_NULL,
        null=True
    )

    total_cost = models.FloatField(
        default=0
    )

    mileage = models.FloatField(
        default=0
    )

    accessories_fee = models.FloatField(
        default=0
    )

    work_fee = models.FloatField(
        default=0
    )

    ticket_type = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    tax_rate = models.FloatField(
        default=0
    )

    description = models.TextField(
        null=True,
        blank=True
    )


class VehicleCheckItem(TimeStampedModel):

    name = models.CharField(
        max_length=100
    )

    is_before_driving_item = models.BooleanField(
        default=False
    )

    is_driving_item = models.BooleanField(
        default=False
    )

    is_after_driving_item = models.BooleanField(
        default=False
    )

    is_published = models.BooleanField(
        default=False
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    objects = models.Manager()
    before_driving_check_items = managers.BeforeDrivingCheckItemsManager()
    driving_check_items = managers.DrivingCheckItemsManager()
    after_driving_check_items = managers.AfterDrivingCheckItemsManager()


class VehicleCheckHistory(TimeStampedModel):

    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='my_vehicle_checks'
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE
    )

    before_driving_problems = models.PositiveIntegerField(
        default=0
    )

    before_driving_description = models.TextField(
        null=True, blank=True
    )

    before_driving_checked_time = models.DateTimeField(
        null=True, blank=True
    )

    driving_problems = models.PositiveIntegerField(
        default=0
    )

    driving_description = models.TextField(
        null=True, blank=True
    )

    driving_checked_time = models.DateTimeField(
        null=True, blank=True
    )

    after_driving_problems = models.PositiveIntegerField(
        default=0
    )

    after_driving_description = models.TextField(
        null=True, blank=True
    )

    after_driving_checked_time = models.DateTimeField(
        null=True, blank=True
    )

    before_driving_checked_items = models.ManyToManyField(
        VehicleCheckItem,
        through='VehicleBeforeDrivingItemCheck',
        through_fields=('vehicle_check_history', 'item'),
        related_name='befores'
    )

    driving_checked_items = models.ManyToManyField(
        VehicleCheckItem,
        through='VehicleDrivingItemCheck',
        through_fields=('vehicle_check_history', 'item'),
        related_name='drivings'
    )

    after_driving_checked_items = models.ManyToManyField(
        VehicleCheckItem,
        through='VehicleAfterDrivingItemCheck',
        through_fields=('vehicle_check_history', 'item'),
        related_name='afters'
    )

    class Meta:
        ordering = ['driver', '-before_driving_checked_time']


class VehicleCheckDocument(models.Model):

    vehicle_check_history = models.ForeignKey(
        VehicleCheckHistory,
        on_delete=models.CASCADE,
        related_name='images'
    )

    document_type = models.CharField(
        max_length=1,
        choices=c.VEHICLE_CHECK_TYPE,
        default=c.VEHICLE_CHECK_TYPE_BEFORE_DRIVING
    )

    document = models.ImageField()


class VehicleBeforeDrivingItemCheck(models.Model):

    vehicle_check_history = models.ForeignKey(
        VehicleCheckHistory,
        on_delete=models.CASCADE
    )

    item = models.ForeignKey(
        VehicleCheckItem,
        on_delete=models.CASCADE
    )

    is_checked = models.BooleanField(
        default=False
    )


class VehicleDrivingItemCheck(models.Model):

    vehicle_check_history = models.ForeignKey(
        VehicleCheckHistory,
        on_delete=models.CASCADE
    )

    item = models.ForeignKey(
        VehicleCheckItem,
        on_delete=models.CASCADE
    )

    is_checked = models.BooleanField(
        default=False
    )


class VehicleAfterDrivingItemCheck(models.Model):

    vehicle_check_history = models.ForeignKey(
        VehicleCheckHistory,
        on_delete=models.CASCADE
    )

    item = models.ForeignKey(
        VehicleCheckItem,
        on_delete=models.CASCADE
    )

    is_checked = models.BooleanField(
        default=False
    )


class VehicleDriverDailyBind(models.Model):

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE
    )

    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='my_vehicle_bind'
    )

    get_on = models.DateTimeField(
        auto_now_add=True
    )

    get_off = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-get_on', 'vehicle']


class VehicleTire(TimeStampedModel):

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE
    )

    position = models.PositiveIntegerField(
        default=0
    )

    class Meta:
        unique_together = [
            'vehicle', 'position'
        ]


class TireManagementHistory(TimeStampedModel):

    vehicle_tire = models.ForeignKey(
        VehicleTire,
        on_delete=models.CASCADE,
        related_name='history'
    )

    installed_on = models.DateField()

    mileage = models.PositiveIntegerField(
        default=0
    )

    mileage_limit = models.PositiveIntegerField(
        default=0
    )

    brand = models.CharField(
        max_length=100
    )

    model = models.CharField(
        max_length=100
    )

    tire_type = models.CharField(
        max_length=100
    )

    tread_depth = models.FloatField(
        default=0
    )

    manufacturer = models.CharField(
        max_length=100
    )

    contact_number = models.CharField(
        max_length=100
    )

    class Meta:
        ordering = [
            '-installed_on',
        ]
