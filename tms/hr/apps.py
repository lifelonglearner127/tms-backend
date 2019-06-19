from django.apps import AppConfig


class HrConfig(AppConfig):
    name = 'tms.hr'

    def ready(self):
        from . import signals # noqa