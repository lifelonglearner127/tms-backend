import redis
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from . import models as m


r = redis.StrictRedis(host='localhost', port=6379, db=15)


@receiver([post_save, post_delete], sender=m.Station)
def notify_asgimqtt_of_station_changes(sender, instance, **kwargs):
    if r.get('station') != b'updated':
        r.set('station', 'updated')
