from django.apps import AppConfig


class OrderConfig(AppConfig):
    name = 'tms.order'

    def ready(self):
        from . import signals   # noqa
