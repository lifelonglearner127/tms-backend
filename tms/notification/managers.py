from django.db import models


class UnreadNotificationManager(models.Manager):
    """
    Pending Job Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            is_read=False
        )


class ReadNotificationManager(models.Manager):
    """
    Pending Job Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            is_read=True
        )


class ProcessedEventManager(models.Manager):
    """
    Pending Job Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            is_processed=True
        )


class PendingEventManager(models.Manager):
    """
    Pending Job Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            is_processed=False
        )
