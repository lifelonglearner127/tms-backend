from django.apps import AppConfig


class JobConfig(AppConfig):
    name = 'tms.job'

    def ready(self):
        from . import signals # noqa
