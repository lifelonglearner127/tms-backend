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


class OilStationManager(models.Manager):
    """
    Admin Model Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            station_type=c.STATION_TYPE_OIL_STATION
        )
