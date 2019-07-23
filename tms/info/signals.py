from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from . import models as m
from ..core.redis import r
from ..core import constants as c


@receiver([post_save, post_delete], sender=m.Station)
def notify_asgimqtt_of_station_changes(sender, instance, **kwargs):
    if instance.station_type == c.STATION_TYPE_BLACK_DOT and\
       r.get('blackdot') != b'updated':
        r.set('blackdot', 'updated')


@receiver(post_delete, sender=m.Station)
def delete_paths(sender, instance, **kwargs):
    m.Route.objects.filter(path__contains=[instance.id]).delete()
