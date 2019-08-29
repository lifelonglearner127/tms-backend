from django.db import models
from month.models import MonthField

from . import managers
from ..core import constants as c

# models
from ..core.models import TimeStampedModel
from ..account.models import User
from ..hr.models import CustomerProfile
from ..info.models import Station, Product
from ..info.models import Route
from ..vehicle.models import Vehicle


class OrderCart(TimeStampedModel):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    weight = models.FloatField(
        default=0
    )

    is_split = models.BooleanField(
        default=False
    )

    is_pump = models.BooleanField(
        default=False
    )


class Order(TimeStampedModel):
    """
    Order model
    """
    alias = models.CharField(
        max_length=100
    )

    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='charge_orders',
        null=True,
        blank=True
    )

    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    order_source = models.CharField(
        max_length=1,
        choices=c.ORDER_SOURCE,
        default=c.ORDER_SOURCE_INTERNAL
    )

    status = models.CharField(
        max_length=1,
        choices=c.ORDER_STATUS,
        default=c.ORDER_STATUS_PENDING
    )

    arrangement_status = models.CharField(
        max_length=1,
        choices=c.TRUCK_ARRANGEMENT_STATUS,
        default=c.TRUCK_ARRANGEMENT_STATUS_PENDING
    )

    invoice_ticket = models.BooleanField(
        default=False
    )

    tax_rate = models.FloatField(
        default=0
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    products = models.ManyToManyField(
        Product,
        through='OrderProduct',
        through_fields=('order', 'product')
    )

    objects = models.Manager()
    pendings = managers.PendingOrderManager()
    inprogress = managers.InProgressOrderManager()
    completeds = managers.CompleteOrderManager()
    from_internal = managers.InternalOrderManager()
    from_customer = managers.CustomerOrderManager()

    @property
    def total_weight(self, instance):
        weight = 0
        for product in instance.orderproduct_set.all():
            weight += product.weight

        return weight

    def __str__(self):
        return self.alias

    class Meta:
        ordering = ['-updated']


class OrderProduct(models.Model):
    """
    Intermediate model for order model and product model
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    weight = models.FloatField(
        default=0
    )

    weight_measure_unit = models.CharField(
        max_length=1,
        choices=c.PRODUCT_WEIGHT_MEASURE_UNIT,
        default=c.PRODUCT_WEIGHT_MEASURE_UNIT_TON
    )

    delivered_weight = models.FloatField(
        default=0
    )

    is_split = models.BooleanField(
        default=False
    )

    is_pump = models.BooleanField(
        default=False
    )


class OrderReport(models.Model):

    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name='monthly_reports'
    )

    month = MonthField()

    orders = models.PositiveIntegerField(
        default=0
    )

    weights = models.FloatField(
        default=0
    )

    class Meta:
        ordering = ('month', )


class Job(models.Model):
    """
    Job model
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='jobs'
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='jobs'
    )

    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='jobs_as_driver'
    )

    escort = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='jobs_as_escort',
    )

    route = models.ForeignKey(
        Route,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    progress = models.PositiveIntegerField(
        default=c.JOB_PROGRESS_NOT_STARTED
    )

    started_on = models.DateTimeField(
        null=True,
        blank=True
    )

    finished_on = models.DateTimeField(
        null=True,
        blank=True
    )

    total_weight = models.FloatField(
        default=0
    )

    total_mileage = models.FloatField(
        default=0
    )

    empty_mileage = models.FloatField(
        default=0
    )

    heavy_mileage = models.FloatField(
        default=0
    )

    highway_mileage = models.FloatField(
        null=True,
        blank=True
    )

    normalway_mileage = models.FloatField(
        null=True,
        blank=True
    )

    is_paid = models.BooleanField(
        default=False
    )

    is_same_station = models.BooleanField(
        default=False
    )

    stations = models.ManyToManyField(
        Station,
        through='JobStation',
        through_fields=('job', 'station')
    )

    @property
    def loading_station(self, instance):
        return instance.stations.all()[0]

    objects = models.Manager()
    completed_jobs = managers.CompleteJobManager()
    progress_jobs = managers.InProgressJobManager()
    pending_jobs = managers.PendingJobManager()


class LoadingStationProductCheck(models.Model):

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='loading_checks'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    weight = models.FloatField(
        default=0
    )


class LoadingStationDocument(models.Model):

    loading_station = models.ForeignKey(
        LoadingStationProductCheck,
        on_delete=models.CASCADE,
        related_name='images'
    )

    document = models.ImageField()


class QualityCheck(models.Model):

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='quality_checks'
    )

    branch = models.PositiveIntegerField(
        default=0
    )

    density = models.FloatField(
        default=0
    )

    additive = models.FloatField(
        default=0
    )


class JobStation(models.Model):

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE
    )

    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE
    )

    due_time = models.DateTimeField()

    step = models.PositiveIntegerField()

    arrived_station_on = models.DateTimeField(
        null=True,
        blank=True
    )

    started_working_on = models.DateTimeField(
        null=True,
        blank=True
    )

    finished_working_on = models.DateTimeField(
        null=True,
        blank=True
    )

    departure_station_on = models.DateTimeField(
        null=True,
        blank=True
    )

    is_completed = models.BooleanField(
        default=False
    )

    products = models.ManyToManyField(
        Product,
        through='JobStationProduct',
        through_fields=('job_station', 'product')
    )

    @property
    def has_next_station(self):
        return self.job.jobstation_set.filter(
            step=self.step+1,
            is_completed=False
        ).exists()

    @property
    def next_station(self):
        return self.job.jobstation_set.filter(
            step=self.step+1,
        ).first()

    @property
    def has_previous_station(self):
        return self.job.jobstation_set.filter(
            step=self.step-1,
            is_completed=False
        ).exists()

    @property
    def previous_station(self):
        return self.job.jobstation_set.filter(
            step=self.step-1
        ).first()

    class Meta:
        ordering = ['job', 'step']


class JobStationProduct(models.Model):

    job_station = models.ForeignKey(
        JobStation,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    branch = models.PositiveIntegerField(
        default=0
    )

    mission_weight = models.FloatField(
        default=0
    )

    volume = models.FloatField(
        default=0
    )

    man_hole = models.CharField(
        max_length=100
    )

    branch_hole = models.CharField(
        max_length=100
    )

    class Meta:
        ordering = ['job_station', 'branch']


class JobStationProductDocument(models.Model):

    job_station_product = models.ForeignKey(
        JobStationProduct,
        on_delete=models.CASCADE,
        related_name='images'
    )

    document = models.ImageField()


class JobReport(models.Model):

    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='report'
    )

    month = MonthField()

    total_mileage = models.PositiveIntegerField(
        default=0
    )

    empty_mileage = models.PositiveIntegerField(
        default=0
    )

    heavy_mileage = models.PositiveIntegerField(
        default=0
    )

    highway_mileage = models.PositiveIntegerField(
        default=0
    )

    normalway_mileage = models.PositiveIntegerField(
        default=0
    )

    def __str__(self):
        return '{}\'s {} report'.format(self.driver, self.month)

    class Meta:
        ordering = ('month', )


class VehicleUserBind(TimeStampedModel):

    vehicle = models.OneToOneField(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='bind'
    )

    driver = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="vehicles_as_driver"
    )

    escort = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="vehicles_as_escort"
    )

    bind_method = models.CharField(
        max_length=1,
        choices=c.VEHICLE_USER_BIND_METHOD,
        default=c.VEHICLE_USER_BIND_METHOD_BY_ADMIN
    )

    objects = models.Manager()
    binds_by_job = managers.JobVehicleUserBindManager()
    binds_by_admin = managers.AdminVehicleUserBindManager()
