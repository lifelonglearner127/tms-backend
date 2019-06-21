from django.db import models
from django.contrib.postgres.fields import ArrayField

from . import managers
from ..core import constants as c
from ..info.models import Station


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
            return Station.loading_stations.get(pk=self.path[0])
        except Station.DoesNotExist:
            return None

    @property
    def quality_station(self):
        try:
            return Station.quality_stations.get(pk=self.path[1])
        except Station.DoesNotExist:
            return None

    @property
    def stations(self):
        points = Station.work_stations.filter(id__in=self.path)
        points = dict([(point.id, point) for point in points])
        return [points[id] for id in self.path]

        # stations = []

        # for point in path:
        #     if point.category == c.POINT_TYPE_LOADING_STATION and \
        #        len(stations) == 0:
        #         try:
        #             station = Station.loading_stations.get(
        #                 longitude=point.longitude,
        #                 latitude=point.latitude
        #             )
        #             stations.append(station)
        #         except Station.DoesNotExist:
        #             break
        #     elif (
        #         point.category == c.POINT_TYPE_QUALITY_STATION and
        #         len(stations) == 1
        #     ):
        #         try:
        #             station = Station.quality_stations.get(
        #                 longitude=point.longitude,
        #                 latitude=point.latitude
        #             )
        #         stations.append(station)
        #         except Station.DoesNotExist:
        #             break

        #     elif (
        #         point.category == c.POINT_TYPE_UNLOADING_STATION and
        #         len(stations) > 1
        #     ):
        #         try:
        #             station = Station.unloading_stations.get(
        #                 longitude=point.longitude,
        #                 latitude=point.latitude
        #             )
        #             stations.append(station)
        #         except Station.DoesNotExist:
        #             break
        #     else:
        #         break

        # return stations

    def __str__(self):
        return self.name
