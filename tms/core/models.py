from django.db import models


class CreatedTimeModel(models.Model):
    """
    Used as base class for models needing create time
    """
    created = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """
    Used as base class for models needing timestamp
    """
    created = models.DateTimeField(
        auto_now_add=True
    )

    updated = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        abstract = True


class ApprovedModel(models.Model):

    request_time = models.DateTimeField(
        auto_now_add=True
    )

    approved = models.BooleanField(
        default=False
    )

    approved_time = models.DateTimeField(
        null=True,
        blank=True
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    class Meta:
        abstract = True
        ordering = ['approved', '-approved_time', '-request_time']


class BasicContactModel(TimeStampedModel):
    """
    Used as base class for models needing basic contact info
    """
    name = models.CharField(
        max_length=100
    )

    contact = models.CharField(
        max_length=100
    )

    mobile = models.CharField(
        max_length=30
    )

    address = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    class Meta:
        abstract = True
