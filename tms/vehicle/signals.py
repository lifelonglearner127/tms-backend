from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from . import models as m
from ..core.redis import r


@receiver([post_save, post_delete], sender=m.Vehicle)
def notify_asgimqtt_of_vehicle_changes(sender, instance, **kwargs):
    if r.get('vehicle') != b'updated':
        r.set('vehicle', 'updated')
