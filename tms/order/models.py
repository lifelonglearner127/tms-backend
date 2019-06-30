from django.db import models
from django.contrib.postgres.fields import ArrayField
from month.models import MonthField

from . import managers
from ..core import constants as c

# models
from ..core.models import TimeStampedModel
from ..account.models import User
from ..info.models import Station, Product
from ..road.models import Route
from ..vehicle.models import Vehicle


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
        null=True
    )

    customer = models.ForeignKey(
        User,
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

    due_time = models.DateTimeField()

    loading_stations = models.ManyToManyField(
        Station,
        through='OrderLoadingStation',
        through_fields=('order', 'loading_station')
    )

    @property
    def products(self):
        products = []
        for order_loading_station in self.orderloadingstation_set.all():
            products.extend(order_loading_station.products.all())

        return products

    @property
    def loading_stations_data(self):
        return self.loading_stations.all()

    @property
    def quality_stations_data(self):
        stations = []
        for order_loading_station in self.orderloadingstation_set.all():
            stations.append(order_loading_station.quality_station)

        return stations

    @property
    def unloading_stations_data(self):
        stations = []
        for order_loading_station in self.orderloadingstation_set.all():
            for order_product in order_loading_station.orderproduct_set.all():
                stations.extend(order_product.unloading_stations.all())

        return stations

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


class OrderLoadingStation(models.Model):
    """
    Intermediate model for order model and loading station
    Currently order has only one loading station, but I create it
    for future business logic
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )

    loading_station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name='loading_stations'
    )

    quality_station = models.ForeignKey(
        Station,
        on_delete=models.SET_NULL,
        related_name='unloading_stations',
        null=True,
        blank=True
    )

    products = models.ManyToManyField(
        Product,
        through='OrderProduct'
    )

    def __str__(self):
        return '{} - Load from {}'.format(
            self.order.alias, self.loading_station.name
        )


class OrderProduct(models.Model):
    """
    Intermediate model for order model and product model
    """
    order_loading_station = models.ForeignKey(
        OrderLoadingStation,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    total_weight = models.DecimalField(
        max_digits=c.WEIGHT_MAX_DIGITS,
        decimal_places=c.WEIGHT_DECIMAL_PLACES,
    )

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

    loss = models.DecimalField(
        max_digits=c.WEIGHT_MAX_DIGITS,
        decimal_places=c.WEIGHT_DECIMAL_PLACES,
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
        through='OrderProductDeliver'
    )

    def __str__(self):
        return 'Order from {}- {} of {}'.format(
            self.order_loading_station.loading_station,
            self.total_weight, self.product.name
        )


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

    due_time = models.DateTimeField()

    weight = models.PositiveIntegerField()

    def __str__(self):
        return 'Order {}: from {} to {}: {} of {}'.format(
            self.order_product.order_loading_station.order,
            self.order_product.order_loading_station.loading_station.name,
            self.unloading_station.name,
            self.weight, self.order_product.total_weight
        )


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

    arrived_loading_station_on = models.DateTimeField(
        null=True,
        blank=True
    )

    started_loading_on = models.DateTimeField(
        null=True,
        blank=True
    )

    finished_loading_on = models.DateTimeField(
        null=True,
        blank=True
    )

    departure_loading_station_on = models.DateTimeField(
        null=True,
        blank=True
    )

    arrived_quality_station_on = models.DateTimeField(
        null=True,
        blank=True
    )

    started_checking_on = models.DateTimeField(
        null=True,
        blank=True
    )

    finished_checking_on = models.DateTimeField(
        null=True,
        blank=True
    )

    departure_quality_station_on = models.DateTimeField(
        null=True,
        blank=True
    )

    finished_on = models.DateTimeField(
        null=True,
        blank=True
    )

    total_weight = models.PositiveIntegerField()

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

    is_paid = models.BooleanField(
        default=False
    )

    missions = models.ManyToManyField(
        OrderProductDeliver,
        through='Mission'
    )

    objects = models.Manager()
    pendings = managers.PendingJobManager()
    inprogress = managers.InProgressJobManager()
    completeds = managers.CompleteJobManager()

    class Meta:
        ordering = (
            'start_due_time',
        )


class Mission(models.Model):

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE
    )

    mission = models.ForeignKey(
        OrderProductDeliver,
        on_delete=models.CASCADE,
        related_name='missions'
    )

    step = models.PositiveIntegerField()

    mission_weight = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    loading_weight = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    unloading_weight = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    arrived_station_on = models.DateTimeField(
        null=True,
        blank=True
    )

    started_unloading_on = models.DateTimeField(
        null=True,
        blank=True
    )

    finished_unloading_on = models.DateTimeField(
        null=True,
        blank=True
    )

    departure_station_on = models.DateTimeField(
        null=True,
        blank=True
    )

    branches = ArrayField(
        models.PositiveIntegerField(),
        default=list
    )

    is_completed = models.BooleanField(
        default=False
    )

    class Meta:
        ordering = ['step']


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
