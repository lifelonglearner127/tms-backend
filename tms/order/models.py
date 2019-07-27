from django.db import models
from django.contrib.postgres.fields import ArrayField
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

    unit_price = models.FloatField(
        default=0
    )

    weight = models.FloatField(
        default=0
    )

    loading_station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name='cart_as_loading_station'
    )

    quality_station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name='cart_as_quality_station'
    )

    unloading_stations = models.ManyToManyField(
        Station,
        through='OrderCartUnloadingStation',
        through_fields=('item', 'unloading_station')
    )


class OrderCartUnloadingStation(models.Model):

    item = models.ForeignKey(
        OrderCart,
        on_delete=models.CASCADE
    )

    unloading_station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE
    )

    weight = models.FloatField(
        default=0
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

    start_due_time = models.DateTimeField(
        null=True,
        blank=True
    )

    finish_due_time = models.DateTimeField(
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

    loading_station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name='orders_as_loading_station'
    )

    quality_station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name='orders_as_quality_station'
    )

    is_same_station = models.BooleanField(
        default=False
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

    total_weight = models.FloatField()

    total_weight_measure_unit = models.CharField(
        max_length=1,
        choices=c.PRODUCT_WEIGHT_MEASURE_UNIT,
        default=c.PRODUCT_WEIGHT_MEASURE_UNIT_TON
    )

    price = models.DecimalField(
        max_digits=c.PRICE_MAX_DIGITS,
        decimal_places=c.PRICE_DECIMAL_PLACES,
        default=0
    )

    price_weight_measure_unit = models.CharField(
        max_length=1,
        choices=c.PRODUCT_WEIGHT_MEASURE_UNIT,
        default=c.PRODUCT_WEIGHT_MEASURE_UNIT_TON
    )

    loss = models.FloatField(
        default=0
    )

    loss_unit = models.CharField(
        max_length=2,
        choices=c.PRODUCT_WEIGHT_MEASURE_UNIT,
        default=c.PRODUCT_WEIGHT_MEASURE_UNIT_TON
    )

    payment_method = models.CharField(
        max_length=1,
        choices=c.PAYMENT_METHOD,
        default=c.PAYMENT_METHOD_TON
    )

    is_split = models.BooleanField(
        default=False
    )

    is_pump = models.BooleanField(
        default=False
    )

    unloading_stations = models.ManyToManyField(
        Station,
        through='OrderProductDeliver',
        through_fields=('order_product', 'unloading_station')
    )

    # def __str__(self):
    #     return 'Order from {}- {} of {}'.format(
    #         self.order_loading_station.loading_station,
    #         self.total_weight, self.product.name
    #     )


class OrderProductDeliver(models.Model):
    """
    Intermediate model for ordered product and unloading station
    """
    order_product = models.ForeignKey(
        OrderProduct,
        on_delete=models.CASCADE
    )

    unloading_station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE
    )

    arriving_due_time = models.DateTimeField(
        null=True,
        blank=True
    )

    weight = models.FloatField()


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

    start_due_time = models.DateTimeField(
        null=True,
        blank=True
    )

    finish_due_time = models.DateTimeField(
        null=True,
        blank=True
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

    bills = models.ManyToManyField(
        'JobBill',
        blank=True
    )

    stations = models.ManyToManyField(
        Station,
        through='JobStation',
        through_fields=('job', 'station')
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

    mission_weight = models.FloatField(
        default=0
    )

    weight = models.FloatField(
        default=0
    )

    document = models.ImageField(
        null=True,
        blank=True
    )

    orderproductdeliver = models.ForeignKey(
        OrderProductDeliver,
        on_delete=models.SET_NULL,
        related_name='job_delivers',
        null=True
    )

    branches = ArrayField(
        models.PositiveIntegerField(),
        default=list
    )


class JobReport(models.Model):

    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='report'
    )

    month = MonthField()

    total_mileage = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    empty_mileage = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    heavy_mileage = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    highway_mileage = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    normalway_mileage = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    def __str__(self):
        return '{}\'s {} report'.format(self.driver, self.month)

    class Meta:
        ordering = ('month', )


class JobBill(TimeStampedModel):

    amount = models.FloatField(
        default=0
    )

    unit_price = models.FloatField(
        default=0
    )

    cost = models.FloatField(
        default=0
    )

    document = models.ImageField(
        null=True,
        blank=True
    )

    category = models.PositiveIntegerField(
        choices=c.BILL_CATEGORY,
        default=c.BILL_FROM_OIL_STATION
    )

    sub_category = models.PositiveIntegerField(
        default=0
    )

    detail_category = models.PositiveIntegerField(
        default=0
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['category', 'sub_category', 'detail_category']


class VehicleUserBind(models.Model):

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE
    )

    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="vehicles_as_driver"
    )

    escort = models.ForeignKey(
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

    class Meta:
        unique_together = (
            'vehicle', 'driver', 'escort'
        )
