from django.db import models

from ..core import constants as c


class LoadingStationManager(models.Manager):
    """
    Admin Model Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            station_type=c.STATION_TYPE_LOADING_STATION
        )


class UnLoadingStationManager(models.Manager):
    """
    Admin Model Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            station_type=c.STATION_TYPE_UNLOADING_STATION
        )


class QualityStationManager(models.Manager):
    """
    Admin Model Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            station_type=c.STATION_TYPE_QUALITY_STATION
        )


class LoadingQualityStationManager(models.Manager):
    """
    Admin Model Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            station_type__in=[
                c.STATION_TYPE_LOADING_STATION,
                c.STATION_TYPE_QUALITY_STATION
            ]
        )


class WorkStationManager(models.Manager):
    """
    Admin Model Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            station_type__in=[
                c.STATION_TYPE_LOADING_STATION, c.STATION_TYPE_QUALITY_STATION,
                c.STATION_TYPE_UNLOADING_STATION
            ]
        )


class OilStationManager(models.Manager):
    """
    Admin Model Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            station_type=c.STATION_TYPE_OIL_STATION
        )


class BlackDotManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            station_type=c.STATION_TYPE_BLACK_DOT
        )


class ParkingStationManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            station_type=c.STATION_TYPE_PARKING_STATION
        )


class GetoffStationManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            station_type=c.STATION_TYPE_GET_OFF_STATION
        )


class RepairStationManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            station_type=c.STATION_TYPE_REPAIR_STATION
        )


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
