from django.apps import AppConfig


class InfoConfig(AppConfig):
    name = 'tms.info'

    def ready(self):
        from . import signals # noqa
