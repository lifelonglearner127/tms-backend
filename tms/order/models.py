from django.db import models
from django.contrib.postgres.fields import ArrayField
from month.models import MonthField
from math import ceil

from . import managers
from ..core import constants as c

# models
from ..core.models import TimeStampedModel, CreatedTimeModel
from ..account.models import User
from ..hr.models import CustomerProfile, StaffProfile
from ..info.models import Station, Product
from ..route.models import Route
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
        max_length=100,
        null=True,
        blank=True
    )

    assignee = models.ForeignKey(
        StaffProfile,
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

    loading_station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name='orders_as_loading_station',
        null=True,
        blank=True
    )

    quality_station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name='orders_as_quality_station',
        null=True,
        blank=True
    )

    loading_due_time = models.DateTimeField(
        null=True,
        blank=True
    )

    is_same_station = models.BooleanField(
        default=False
    )

    route = models.ForeignKey(
        Route,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    products = models.ManyToManyField(
        Product,
        through='OrderProduct',
        through_fields=('order', 'product')
    )

    is_deleted = models.BooleanField(
        default=False
    )

    objects = models.Manager()
    availables = managers.AvailableOrderManager()
    deleteds = managers.DeletedOrderManager()
    pendings = managers.PendingOrderManager()
    inprogress = managers.InProgressOrderManager()
    completeds = managers.CompleteOrderManager()
    from_internal = managers.InternalOrderManager()
    from_customer = managers.CustomerOrderManager()

    @property
    def total_weight(self):
        weight = 0
        for product in self.orderproduct_set.all():
            weight += product.weight

        return weight

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

    # sum of arranged weight
    arranged_weight = models.FloatField(
        default=0
    )

    # summ of delivered weights
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
        ordering = ('-month', )


def days_hours_minutes(td):
    seconds = (td.seconds//60) % 60
    seconds += td.microseconds / 1e6
    return td.days, td.seconds//3600, seconds


def format_hms_string(time_diff, format_string):
    format_string = "{}: ".format(format_string)
    days, hours, mins = days_hours_minutes(time_diff)
    if days > 0:
        format_string += "{}天 ".format(days)
    if hours > 0:
        format_string += "{}小时 ".format(hours)
    if mins > 0:
        format_string += "{}分钟".format(ceil(mins))
    if mins == 0:
        format_string += "0分钟"
    return format_string


class Job(TimeStampedModel):
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

    routes = ArrayField(
        models.PositiveIntegerField()
    )

    rest_place = models.ForeignKey(
        Station,
        on_delete=models.SET_NULL,
        null=True,
        related_name='jobs_as_rest_place'
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

    stations = models.ManyToManyField(
        Station,
        through='JobStation',
        through_fields=('job', 'station')
    )

    associated_workers = models.ManyToManyField(
        User,
        related_name='associated_jobs',
        through='JobWorker',
        through_fields=('job', 'worker')
    )

    @property
    def products(self):
        loading_station = self.jobstation_set.first()
        return loading_station.products.distinct()

    @property
    def total_mission_weight(self):
        loading_station = self.jobstation_set.first()
        total_mission_weight = 0

        if loading_station is not None:
            for product in loading_station.jobstationproduct_set.all():
                total_mission_weight += product.mission_weight

        return total_mission_weight

    @property
    def total_delivered_weight(self):
        total_delivered_weight = 0

        for station in self.jobstation_set.all()[2:]:
            for product in station.jobstationproduct_set.all():
                total_delivered_weight += product.weight

        return total_delivered_weight

    @property
    def freight_payment_to_driver(self):
        return self.total_mission_weight * self.heavy_mileage * 0.4

    @property
    def to_loading_station_time_duration(self):
        station = self.jobstation_set.first()
        duration = 0
        if self.started_on is not None and station.started_working_on is not None:
            duration = (station.arrived_station_on - self.started_on).total_seconds()

        return round(duration / 3600, 1)

    @property
    def waiting_at_loading_station_time_duration(self):
        station = self.jobstation_set.first()
        duration = 0
        if station.arrived_station_on is not None and station.started_working_on is not None:
            duration = (station.started_working_on - station.arrived_station_on).total_seconds()

        return round(duration / 3600, 1)

    @property
    def loading_time_duration(self):
        station = self.jobstation_set.first()
        duration = 0
        if station.started_working_on is not None and station.finished_working_on is not None:
            duration = (station.finished_working_on - station.started_working_on).total_seconds()

        return round(duration / 3600, 1)

    @property
    def waiting_at_loading_station_after_loading_time_duration(self):
        station = self.jobstation_set.first()
        duration = 0
        if station.departure_station_on is not None and station.finished_on is not None:
            duration = (station.departure_station_on - station.finished_on).total_seconds()

        return round(duration / 3600, 1)

    @property
    def to_quality_station_time_duration(self):
        loading_station = self.jobstation_set.first()
        quality_station = self.jobstation_set.get(step=1)
        duration = 0
        if loading_station.departure_station_on is not None and quality_station.arrived_station_on is not None:
            duration = (quality_station.arrived_station_on - loading_station.departure_station_on).total_seconds()

        return round(duration / 3600, 1)

    @property
    def waiting_at_quality_station_time_duration(self):
        station = self.jobstation_set.get(step=1)
        duration = 0
        if station.arrived_station_on is not None and station.started_working_on is not None:
            duration = (station.started_working_on - station.arrived_station_on).total_seconds()

        return round(duration / 3600, 1)

    @property
    def quality_time_duration(self):
        station = self.jobstation_set.get(step=1)
        duration = 0
        if station.started_working_on is not None and station.finished_working_on is not None:
            duration = (station.finished_working_on - station.started_working_on).total_seconds()

        return round(duration / 3600, 1)

    @property
    def waiting_at_quality_station_after_quality_time_duration(self):
        station = self.jobstation_set.get(step=1)
        duration = 0
        if station.finished_working_on is not None and station.departure_station_on is not None:
            duration = (station.departure_station_on - station.finished_working_on).total_seconds()

        return round(duration / 3600, 1)

    @property
    def unloading_time_duration(self):
        duration = 0
        for station in self.jobstation_set.all()[2:]:
            if station.started_working_on is None or station.finished_working_on is None:
                continue
            duration += (station.finished_working_on - station.started_working_on).total_seconds()

        return round(duration / 3600, 1)

    @property
    def total_time_duration(self):
        return self.loading_time_duration + self.quality_time_duration + self.unloading_time_duration

    @property
    def active_job_driver(self):
        return self.jobworker_set.filter(worker_type=c.WORKER_TYPE_DRIVER, is_active=True).first()

    @property
    def next_candidate_job_driver(self):
        return self.jobworker_set.filter(worker_type=c.WORKER_TYPE_DRIVER).order_by('-assigned_on').first()

    @property
    def active_job_escort(self):
        return self.jobworker_set.filter(worker_type=c.WORKER_TYPE_ESCORT, is_active=True).first()

    @property
    def next_candidate_job_escort(self):
        return self.jobworker_set.filter(worker_type=c.WORKER_TYPE_ESCORT).order_by('-assigned_on').first()

    objects = models.Manager()
    completed_jobs = managers.CompleteJobManager()
    progress_jobs = managers.InProgressJobManager()
    pending_jobs = managers.PendingJobManager()

    class Meta:
        ordering = (
            '-finished_on',
        )


class JobWorker(models.Model):

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE
    )

    worker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='job'
    )

    worker_type = models.CharField(
        max_length=1,
        choices=c.WORKER_TYPE,
        default=c.WORKER_TYPE_DRIVER
    )

    started_on = models.DateTimeField(
        null=True,
        blank=True
    )

    finished_on = models.DateTimeField(
        null=True,
        blank=True
    )

    start_due_time = models.DateTimeField(
        null=True,
        blank=True
    )

    start_place = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )

    assigned_on = models.DateTimeField(
        auto_now_add=True
    )

    is_active = models.BooleanField(
        default=False
    )

    objects = models.Manager()
    drivers = managers.JobWorkerDriverManager()
    escorts = managers.JobWorkerEscortManager()

    class Meta:
        ordering = (
            'job', '-is_active', '-assigned_on',
        )


class LoadingStationProductCheck(CreatedTimeModel):

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

    volume = models.FloatField(
        default=0
    )


class JobStation(models.Model):

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE
    )

    station = models.ForeignKey(
        Station,
        on_delete=models.SET_NULL,
        null=True
    )

    transport_unit_price = models.FloatField(
        default=0
    )

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

    @property
    def due_time(self):
        return self.jobstationproduct_set.first().due_time

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

    due_time = models.DateTimeField(
        null=True,
        blank=True
    )

    branch = models.PositiveIntegerField(
        default=0
    )

    mission_weight = models.FloatField(
        default=0
    )

    weight = models.FloatField(
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
        ordering = ('-month', )


class OrderPayment(TimeStampedModel):

    job_station = models.ForeignKey(
        JobStation,
        on_delete=models.CASCADE
    )

    distance = models.FloatField(
        default=0
    )

    adjustment = models.FloatField(
        default=0
    )

    status = models.PositiveIntegerField(
        choices=c.ORDER_PAYMENT_STATUS,
        default=c.ORDER_PAYMENT_STATUS_NO_DISTANCE
    )

    @property
    def loading_station_volume(self):
        total_volume = 0
        for product in self.job_station.jobstationproduct_set.all():
            total_volume += product.volume

        return total_volume

    @property
    def unloading_station_volume(self):
        total_volume = 0
        for product in self.job_station.jobstationproduct_set.all():
            total_volume += product.volume

        return total_volume

    @property
    def total_price(self):
        return self.distance * self.job_station.transport_unit_price * self.unloading_station_volume - self.adjustment
