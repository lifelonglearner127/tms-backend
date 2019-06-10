from django.db import models

from ..core import constants as c


class LoadingStationPointManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            category=c.POINT_TYPE_LOADING_STATION
        )


class UnLoadingStationPointManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            category=c.POINT_TYPE_UNLOADING_STATION
        )


class QualityStationPointManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            category=c.POINT_TYPE_QUALITY_STATION
        )


class OilStationPointManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            category=c.POINT_TYPE_OIL_STATION
        )


class StationPointManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            category__in=[
                c.POINT_TYPE_LOADING_STATION, c.POINT_TYPE_UNLOADING_STATION,
                c.POINT_TYPE_QUALITY_STATION, c.POINT_TYPE_OIL_STATION
            ]
        )


class BlackDotPointManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            category=c.POINT_TYPE_BLACK_DOT
        )
