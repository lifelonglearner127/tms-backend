from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import (
    LoadingStation, UnLoadingStation, QualityStation, OilStation
)
from ..road.models import Point


@receiver(post_save, sender=LoadingStation)
def save_loading_station_position(sender, instance, **kwargs):
    Point.objects.create(
        name=instance.name,
        address=instance.address,
        latitude=instance.latitude,
        longitude=instance.longitude
    )


@receiver(post_save, sender=UnLoadingStation)
def save_unloading_station_position(sender, instance, **kwargs):
    Point.objects.create(
        name=instance.name,
        address=instance.address,
        latitude=instance.latitude,
        longitude=instance.longitude
    )


@receiver(post_save, sender=QualityStation)
def save_quality_station_position(sender, instance, **kwargs):
    Point.objects.create(
        name=instance.name,
        address=instance.address,
        latitude=instance.latitude,
        longitude=instance.longitude
    )


@receiver(post_save, sender=OilStation)
def save_oil_station_position(sender, instance, **kwargs):
    Point.objects.create(
        name=instance.name,
        address=instance.address,
        latitude=instance.latitude,
        longitude=instance.longitude
    )
