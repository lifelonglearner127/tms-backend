from django.db import models
from django.db.models import Q

from ..core import constants as c


class AdminUserManager(models.Manager):
    """
    Admin Model Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(role=c.USER_ROLE_ADMIN)


class StaffUserManager(models.Manager):
    """
    Staff Model Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            role__in=[c.USER_ROLE_ADMIN, c.USER_ROLE_STAFF]
        )


class DriverUserManager(models.Manager):
    """
    Driver Model Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(role=c.USER_ROLE_DRIVER)


class EscortUserManager(models.Manager):
    """
    Escort Model Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(role=c.USER_ROLE_ESCORT)


class CustomerUserManager(models.Manager):
    """
    Customer Model Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(role=c.USER_ROLE_CUSTOMER)


class CompanyMemberUserManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            role__in=[
                c.USER_ROLE_ADMIN, c.USER_ROLE_STAFF,
                c.USER_ROLE_DRIVER, c.USER_ROLE_ESCORT
            ]
        )
