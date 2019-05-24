from django.db import models
from django.contrib.postgres.fields import ArrayField

from ..core import constants


class BasePoint(models.Model):

    latitude = models.FloatField()

    longitude = models.FloatField()

    name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    address = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    class Meta:
        abstract = True


class Point(BasePoint):

    def __str__(self):
        return '{}: ({},{})'.format(
            self.name, self.latitude, self.longitude
        )


class BlackPoint(BasePoint):

    category = models.CharField(
        max_length=1,
        choices=constants.BLACKDOT_TYPE,
        default=constants.BLACKDOT_TYPE_ROAD_REPAIR
    )

    def __str__(self):
        return 'Black Point - {}: ({},{})'.format(
            self.latitude, self.longitude, self.name
        )


class Route(models.Model):

    name = models.CharField(
        max_length=100,
    )

    # current map api allow only 16 waypoints
    path = ArrayField(
        models.PositiveIntegerField(),
        size=18
    )

    policy = models.PositiveIntegerField()

    distance = models.PositiveIntegerField()

    def __str__(self):
        return self.name
