from django.apps import AppConfig


class VehicleConfig(AppConfig):
    name = 'tms.vehicle'

    def ready(self):
        from . import signals # noqa
