from django.db import models

from ..core import constants


class AdminManager(models.Manager):
    """
    Admin Model Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(role=constants.USER_ROLE_ADMIN)


class StaffManager(models.Manager):
    """
    Staff Model Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            role__in=[constants.USER_ROLE_ADMIN, constants.USER_ROLE_STAFF]
        )


class DriverManager(models.Manager):
    """
    Driver Model Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(role=constants.USER_ROLE_DRIVER)


class EscortManager(models.Manager):
    """
    Escort Model Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(role=constants.USER_ROLE_ESCORT)


class CustomerManager(models.Manager):
    """
    Customer Model Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(role=constants.USER_ROLE_CUSTOMER)


class StaffDriverManager(models.Manager):
    """
    Driver staff manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            user__role=constants.USER_ROLE_DRIVER
        )


class StaffEscortManager(models.Manager):
    """
    Escort staff manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            user__role=constants.USER_ROLE_ESCORT
        )
