from django.apps import AppConfig


class BusinessConfig(AppConfig):
    name = 'tms.business'

    def ready(self):
        from . import signals # noqa
