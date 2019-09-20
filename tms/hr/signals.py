from django.dispatch import receiver
from django.db.models.signals import post_delete

from . import models as m


@receiver(post_delete, sender=m.StaffProfile)
def auto_delete_use_with_staffprofile(sender, instance, **kwargs):
    instance.user.delete()
