from django.db import models
from django.contrib.postgres.fields import ArrayField
from month.models import MonthField
from datetime import timedelta
from math import ceil

from . import managers
from ..core import constants as c

# models
from ..core.models import TimeStampedModel
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

    objects = models.Manager()
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

    routes = ArrayField(
        models.PositiveIntegerField()
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

    stations = models.ManyToManyField(
        Station,
        through='JobStation',
        through_fields=('job', 'station')
    )

    associated_drivers = models.ManyToManyField(
        User,
        related_name='associated_drivers',
        through='JobDriver',
        through_fields=('job', 'driver')
    )

    associated_escorts = models.ManyToManyField(
        User,
        related_name='associated_escorts',
        through='JobEscort',
        through_fields=('job', 'escort')
    )

    @property
    def stations_info(self):
        stations = self.stations.all()
        station_info = []
        previous_station_time = self.started_on
        for station in stations:
            jobstation = station.jobstation_set.get(job=self)
            if station.station_type == 'L':
                arrival_format_string = '赶往装货地时长'
                loadwait_format_string = '等待装货时长'
                load_format_string = '装货时长'
            elif station.station_type == 'Q':
                arrival_format_string = '赶往质检地时长'
                loadwait_format_string = '等待质检时长'
                load_format_string = '质检时长'
            else:
                arrival_format_string = '赶往卸货地时长'
                loadwait_format_string = '等待卸货时长'
                load_format_string = '卸货时长'

            if jobstation.arrived_station_on:
                time_diff = jobstation.arrived_station_on - previous_station_time
                arrive_duration = format_hms_string(time_diff, arrival_format_string)
            else:
                arrive_duration = '{}: 未知'.format(arrival_format_string)

            if jobstation.started_working_on and jobstation.arrived_station_on:
                time_diff = jobstation.started_working_on - jobstation.arrived_station_on
                load_wait_duration = format_hms_string(time_diff, loadwait_format_string)
            else:
                load_wait_duration = '{}: 未知'.format(loadwait_format_string)
            if jobstation.started_working_on and jobstation.finished_working_on:
                time_diff = jobstation.finished_working_on - jobstation.started_working_on
                load_duration = format_hms_string(time_diff, load_format_string)
            else:
                load_duration = '{}: 未知'.format(load_format_string)

            previous_station_time = jobstation.departure_station_on
            station_info.append({
                'arrive_duration': arrive_duration,
                'load_wait_duration': load_wait_duration,
                'load_duration': load_duration
            })
        return station_info

    @property
    def unloading_stations_product(self):

        unloading_stations = self.stations.all()[2:]
        unloading_station_products = []
        for u_station in unloading_stations:
            jobstation = u_station.jobstation_set.get(job=self)
            job_station_product = jobstation.jobstationproduct_set.get()
            unloading_station_products.append({
                'jobstation': jobstation.station.name,
                'product': job_station_product.product.name,
                'mission_weight': job_station_product.mission_weight,
                'volume': job_station_product.volume
            })
        return unloading_station_products

    @property
    def unloading_stations_consume_weight(self):

        unloading_stations = self.stations.all()[2:]
        total_consume_weight = 0
        for u_station in unloading_stations:
            jobstation = u_station.jobstation_set.get(job=self)
            job_station_product = jobstation.jobstationproduct_set.get()
            total_consume_weight = total_consume_weight + job_station_product.mission_weight - job_station_product.volume
        return total_consume_weight

    @property
    def road_duration(self):

        job_duration = timedelta()
        road_time = timedelta()
        if self.finished_on and self.started_on:
            job_duration = self.finished_on - self.started_on
            road_time = job_duration
        if job_duration.microseconds > 0:
            stations = self.stations.all()
            for station in stations:
                station_duration = timedelta()
                jobstation = station.jobstation_set.get(job=self)
                if jobstation.arrived_station_on and jobstation.departure_station_on:
                    station_duration = jobstation.departure_station_on - jobstation.arrived_station_on
                road_time = road_time - station_duration
        road_time_string = format_hms_string(road_time, "在途时间")
        return road_time_string

    @property
    def operating_efficiency(self):
        total_mileage = self.total_mileage
        print(total_mileage)

        if self.finished_on and self.started_on:
            diff = self.finished_on - self.started_on
            job_duration = diff.days * 24 * 60 * 60 + diff.seconds * 1000 + diff.microseconds
            print(job_duration)
            if job_duration == 0:
                result_string = "未知"
            else:
                result_string = "{:.2f}".format(total_mileage / job_duration)
                print(result_string)
        else:
            result_string = "未知"

        return result_string

    @property
    def drained_oil(self):

        total_weight = self.total_weight
        unloading_total_duration = timedelta()
        unloading_stations = self.stations.all()[2:]
        for u_station in unloading_stations:
            station_unloading_time = timedelta()
            job_station = u_station.jobstation_set.get(job=self)
            if job_station.arrived_station_on and job_station.started_working_on:
                station_unloading_time = station_unloading_time + job_station.started_working_on - job_station.arrived_station_on
            if job_station.started_working_on and job_station.finished_working_on:
                station_unloading_time = station_unloading_time + job_station.finished_working_on - job_station.started_working_on
            unloading_total_duration = unloading_total_duration + station_unloading_time
        print(unloading_total_duration)
        duration = unloading_total_duration.days * 24 * 60 * 60 + unloading_total_duration.seconds * 1000 + unloading_total_duration.microseconds
        if duration == 0:
            result_string = "未知"
        else:
            result_string = "{:.2f}".format(total_weight * 60 * 1000 / duration)
        return result_string

    @property
    def turnover(self):
        return self.total_weight * self.heavy_mileage * 0.4

    objects = models.Manager()
    completed_jobs = managers.CompleteJobManager()
    progress_jobs = managers.InProgressJobManager()
    pending_jobs = managers.PendingJobManager()

    class Meta:
        ordering = (
            '-finished_on',
        )


class JobDriver(models.Model):

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE
    )

    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='jobs_as_driver'
    )

    started_on = models.DateTimeField(
        null=True,
        blank=True
    )

    finished_on = models.DateTimeField(
        null=True,
        blank=True
    )

    assigned_on = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = (
            'job', '-assigned_on',
        )


class JobEscort(models.Model):

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE
    )

    escort = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='jobs_as_escorts'
    )

    started_on = models.DateTimeField(
        null=True,
        blank=True
    )

    finished_on = models.DateTimeField(
        null=True,
        blank=True
    )

    assigned_on = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = (
            'job', '-assigned_on',
        )


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
        on_delete=models.SET_NULL,
        null=True
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
        ordering = ('-month', )
