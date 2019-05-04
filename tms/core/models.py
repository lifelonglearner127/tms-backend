from django.db import models


class CreatedTimeModel(models.Model):

    created = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        abstract = True
        ordering = ['-created']


class TimeStampedModel(models.Model):

    created = models.DateTimeField(
        auto_now_add=True
    )

    updated = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        abstract = True
        ordering = ['-created']


class BasicContactModel(TimeStampedModel):

    name = models.CharField(
        max_length=100
    )

    contact = models.CharField(
        max_length=100
    )

    phone_number = models.CharField(
        max_length=30
    )

    address = models.CharField(
        max_length=100
    )

    class Meta:
        abstract = True
