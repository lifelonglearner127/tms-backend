from django.db import models
from django.contrib.postgres.fields import ArrayField

from ..core import constants as c
from ..info.models import Station


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

    category = models.CharField(
        max_length=1,
        choices=c.POINT_TYPE,
        default=c.POINT_TYPE_LOADING_STATION
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
        choices=c.BLACKDOT_TYPE,
        default=c.BLACKDOT_TYPE_ROAD_REPAIR
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
                    station = Station.loading_stations.get(
                        longitude=point.longitude,
                        latitude=point.latitude
                    )
                    stations.append({'loading_station': station})
                except Station.DoesNotExist:
                    break
            elif (
                point.category == c.POINT_TYPE_QUALITY_STATION and
                len(stations) == 1
            ):
                try:
                    station = Station.quality_stations.get(
                        longitude=point.longitude,
                        latitude=point.latitude
                    )
                    stations.append({'quality_station': station})
                except Station.DoesNotExist:
                    break

            elif (
                point.category == c.POINT_TYPE_UNLOADING_STATION and
                len(stations) > 1
            ):
                try:
                    station = Station.unloading_stations.get(
                        longitude=point.longitude,
                        latitude=point.latitude
                    )
                    stations.append({'unloading_station': station})
                except Station.DoesNotExist:
                    break
            else:
                break

        return stations

    def __str__(self):
        return self.name
