from django.db import models
from django.contrib.postgres.fields import ArrayField

from . import managers
from ..core import constants as c
from ..core.models import TimeStampedModel
from ..info.models import Station


class Point(TimeStampedModel):

    name = models.CharField(
        max_length=100
    )

    latitude = models.FloatField(
        null=True,
        blank=True
    )

    longitude = models.FloatField(
        null=True,
        blank=True
    )

    category = models.CharField(
        max_length=1,
        choices=c.POINT_TYPE,
        default=c.POINT_TYPE_LOADING_STATION
    )

    notification_message = models.TextField(
        null=True,
        blank=True
    )

    objects = models.Manager()
    loading = managers.LoadingStationPointManager()
    unloading = managers.UnLoadingStationPointManager()
    quality = managers.QualityStationPointManager()
    oil = managers.OilStationPointManager()
    station = managers.StationPointManager()
    black = managers.BlackDotPointManager()

    class Meta:
        ordering = ['-updated']

    def __str__(self):
        return '{} - {} type'.format(self.name, self.category)


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

    @property
    def loading_station(self):
        try:
            pt = Point.objects.get(pk=self.path[0])
            return Station.loading.get(
                longitude=pt.longitude,
                latitude=pt.latitude
            )
        except Point.DoesNotExist:
            return None
        except Station.DoesNotExist:
            return None

    @property
    def quality_station(self):
        try:
            pt = Point.objects.get(pk=self.path[1])
            return Station.quality.get(
                longitude=pt.longitude,
                latitude=pt.latitude
            )
        except Point.DoesNotExist:
            return None
        except Station.DoesNotExist:
            return None

    @property
    def stations(self):
        points = Point.objects.filter(id__in=self.path)
        points = dict([(point.id, point) for point in points])
        path = [points[id] for id in self.path]

        stations = []

        for point in path:
            if point.category == c.POINT_TYPE_LOADING_STATION and \
               len(stations) == 0:
                try:
                    station = Station.loading.get(
                        longitude=point.longitude,
                        latitude=point.latitude
                    )
                    stations.append(station)
                except Station.DoesNotExist:
                    break
            elif (
                point.category == c.POINT_TYPE_QUALITY_STATION and
                len(stations) == 1
            ):
                try:
                    station = Station.quality.get(
                        longitude=point.longitude,
                        latitude=point.latitude
                    )
                    stations.append(station)
                except Station.DoesNotExist:
                    break

            elif (
                point.category == c.POINT_TYPE_UNLOADING_STATION and
                len(stations) > 1
            ):
                try:
                    station = Station.unloading.get(
                        longitude=point.longitude,
                        latitude=point.latitude
                    )
                    stations.append(station)
                except Station.DoesNotExist:
                    break
            else:
                break

        return stations

    def __str__(self):
        return self.name
