from django.db import models

from ..core import constants as c
from ..core.models import ApprovedModel
from ..account.models import StaffProfile


class RestRequest(ApprovedModel):

    staff = models.ForeignKey(
        StaffProfile,
        on_delete=models.CASCADE
    )

    category = models.CharField(
        max_length=1
    )

    from_date = models.DateField()

    to_date = models.DateField()


class Department(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['name']


class Position(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['name']


class RoleManagement(models.Model):

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )

    position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE
    )

    permission = models.PositiveIntegerField(
        choices=c.PERMISSION_TYPE,
        default=c.PERMISSION_TYPE_NO
    )

    class Meta:
        ordering = ['department', 'position']
        unique_together = ['department', 'position']
