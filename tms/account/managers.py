from django.db import models

from ..core import constants as c


class AdminUserManager(models.Manager):
    """
    Admin Model Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(user_type=c.USER_TYPE_ADMIN)


class StaffUserManager(models.Manager):
    """
    Staff Model Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            user_type__in=[c.USER_TYPE_ADMIN, c.USER_TYPE_STAFF]
        )


class DriverUserManager(models.Manager):
    """
    Driver Model Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(user_type=c.USER_TYPE_DRIVER)


class EscortUserManager(models.Manager):
    """
    Escort Model Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(user_type=c.USER_TYPE_ESCORT)


class WheelUserManager(models.Manager):
    """
    Escort Model Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(user_type__in=[
            c.USER_TYPE_DRIVER, c.USER_TYPE_ESCORT
        ])


class CustomerUserManager(models.Manager):
    """
    Customer Model Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(user_type=c.USER_TYPE_CUSTOMER)


class SecurityOfficerUserManager(models.Manager):
    """
    Customer Model Manager
    """
    def get_queryset(self):
        return super().get_queryset().filter(user_type=c.USER_TYPE_SECURITY_OFFICER)


class CompanyMemberUserManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            user_type__in=[
                c.USER_TYPE_ADMIN, c.USER_TYPE_STAFF,
                c.USER_TYPE_DRIVER, c.USER_TYPE_ESCORT
            ]
        )
