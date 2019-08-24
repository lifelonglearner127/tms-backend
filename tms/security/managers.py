from django.db import models


class PublishedContentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            is_published=True
        )


class UnPublishedContentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            is_published=False
        )
