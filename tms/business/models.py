from django.db import models

from ..core import constants as c

# models
from ..core.models import ApprovedModel
from ..account.models import User
from ..order.models import Job
from ..vehicle.models import Vehicle


class ParkingRequest(ApprovedModel):

    job = models.ForeignKey(
        Job,
        on_delete=models.SET_NULL,
        null=True
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='parking_requests'
    )

    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='parking_requests_as_driver'
    )

    escort = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='parking_requests_as_escort'
    )

    place = models.CharField(
        max_length=100
    )


class DriverChangeRequest(ApprovedModel):

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE
    )

    old_driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='driver_change_requests'
    )

    new_driver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='driver_change_assigned'
    )

    change_time = models.DateTimeField(
        null=True,
        blank=True
    )

    change_place = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['approved', '-approved_time', '-request_time']
        unique_together = ['job', 'old_driver']


class EscortChangeRequest(ApprovedModel):

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE
    )

    old_escort = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='escort_change_requests'
    )

    new_escort = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='escort_change_assigned'
    )

    change_time = models.DateTimeField(
        null=True,
        blank=True
    )

    change_place = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['approved', '-approved_time', '-request_time']
        unique_together = ['job', 'old_escort']


class RestRequest(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='my_rest_request'
    )

    category = models.CharField(
        max_length=1,
        choices=c.REST_REQUEST_CATEGORY,
        default=c.REST_REQUEST_ILL
    )

    from_date = models.DateField()

    to_date = models.DateField()

    request_time = models.DateTimeField(
        auto_now_add=True
    )

    approved = models.BooleanField(
        default=False
    )

    approved_time = models.DateTimeField(
        null=True,
        blank=True
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    approvers = models.ManyToManyField(
        User,
        through='RestRequestApprover',
        through_fields=('rest_request', 'approver'),
        related_name='rest_request_as_approver'
    )

    ccs = models.ManyToManyField(
        User,
        through='RestRequestCC',
        through_fields=('rest_request', 'cc'),
        related_name='rest_request_as_cc'
    )

    @property
    def approvers_count(self):
        return self.approvers.all().count()

    class Meta:
        ordering = ['approved', '-approved_time', '-request_time']
        # unique_together = ['user', 'from_date', 'to_date']


class RestRequestApprover(models.Model):

    rest_request = models.ForeignKey(
        RestRequest,
        on_delete=models.CASCADE
    )

    approver_type = models.CharField(
        max_length=1,
        choices=c.APPROVER_TYPE,
        default=c.APPROVER_TYPE_MEMBER
    )

    approver = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    approved = models.BooleanField(
        default=False
    )

    approved_time = models.DateTimeField(
        auto_now=True
    )

    step = models.PositiveIntegerField(
        default=0
    )

    description = models.TextField(
        null=True, blank=True
    )


class RestRequestCC(models.Model):

    rest_request = models.ForeignKey(
        RestRequest,
        on_delete=models.CASCADE
    )

    cc_type = models.CharField(
        max_length=1,
        choices=c.CC_TYPE,
        default=c.CC_TYPE_MEMBER
    )

    cc = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    is_read = models.BooleanField(
        default=False
    )

    read_time = models.DateTimeField(
        auto_now=True
    )
