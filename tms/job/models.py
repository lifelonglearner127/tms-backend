from django.db import models

from . import managers
from ..core import constants as c
from ..account.models import DriverProfile, EscortProfile
from ..vehicle.models import Vehicle
from ..order.models import Order, OrderProductDeliver
from ..road.models import Route


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
        DriverProfile,
        on_delete=models.CASCADE,
        related_name='jobs'
    )

    escort = models.ForeignKey(
        EscortProfile,
        on_delete=models.CASCADE,
        related_name='jobs',
    )

    route = models.ForeignKey(
        Route,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    progress = models.PositiveIntegerField(
        choices=c.JOB_PROGRESS,
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

    missions = models.ManyToManyField(
        OrderProductDeliver,
        through='Mission'
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

    objects = models.Manager()
    pendings = managers.PendingJobManager()
    inprogress = managers.InProgressJobManager()
    completeds = managers.CompleteJobManager()


class Mission(models.Model):

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE
    )

    mission = models.ForeignKey(
        OrderProductDeliver,
        on_delete=models.CASCADE
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

    is_completed = models.BooleanField(
        default=False
    )

    class Meta:
        ordering = ['step']


class JobBillDocument(models.Model):

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='bills'
    )

    document = models.ImageField()

    category = models.CharField(
        max_length=1,
        choices=c.BILL_TYPE,
        default=c.BILL_FROM_LOADING_STATION
    )

    def __str__(self):
        return self.get_category_display()


class DriverNotification(models.Model):

    driver = models.ForeignKey(
        DriverProfile,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    message = models.TextField()

    sent = models.DateTimeField(
        auto_now_add=True
    )

    is_read = models.BooleanField(
        default=False
    )

    def __str__(self):
        return 'Meessage to {} at {}'.format(
            self.driver.user.username, self.sent
        )
