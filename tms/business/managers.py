from django.db import models


class ApprovedRequestsManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(approved=True)


class UnApprovedRequestsManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(approved=False)
