from django.db import models


class ActiveRequestsManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_cancelled=False)


class CancelledRequestsManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_cancelled=True)


class ApprovedRequestsManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_cancelled=False, approved=True)


class UnApprovedRequestsManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_cancelled=False, approved=False)
