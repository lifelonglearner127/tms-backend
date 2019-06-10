from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import Station
from ..road.models import Point


@receiver(post_save, sender=Station)
def save_station_position(sender, instance, **kwargs):
    Point.objects.update_or_create(
        latitude=instance.latitude,
        longitude=instance.longitude,
        category=instance.station_type,
        defaults={'name': instance.name}
    )
