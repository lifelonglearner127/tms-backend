from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from . import models as m
from ..core.redis import r


@receiver([post_save, post_delete], sender=m.Station)
def notify_asgimqtt_of_station_changes(sender, instance, **kwargs):
    if r.get('station') != b'updated':
        r.set('station', 'updated')


@receiver(post_delete, sender=m.Station)
def delete_paths(sender, instance, **kwargs):
    m.Route.objects.filter(path__contains=[instance.id]).delete()
