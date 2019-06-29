from django.db import models
from django.contrib.postgres.fields import ArrayField

from ..core import constants as c
from ..core.models import TimeStampedModel
from ..info.models import Station


class Route(TimeStampedModel):

    name = models.CharField(
        max_length=100,
    )

    # current map api allow only 16 waypoints
    path = ArrayField(
        models.PositiveIntegerField(),
        size=18
    )

    policy = models.PositiveIntegerField(
        choices=c.ROUTE_PLANNING_POLICY,
        default=c.ROUTE_PLANNING_POLICY_LEAST_TIME
    )

    distance = models.PositiveIntegerField()

    @property
    def loading_station(self):
        try:
            return Station.loadingstations.get(pk=self.path[0])
        except Station.DoesNotExist:
            return None

    @property
    def quality_station(self):
        try:
            return Station.qualitystations.get(pk=self.path[1])
        except Station.DoesNotExist:
            return None

    @property
    def stations(self):
        points = Station.workstations.filter(id__in=self.path)
        points = dict([(point.id, point) for point in points])
        return [points[id] for id in self.path]

    @property
    def stations_count(self):
        return Station.workstations.filter(id__in=self.path).count()

    def __str__(self):
        return self.name
