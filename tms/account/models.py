from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager

from ..core import constants
from ..core.validations import validate_phone_number


class AdminManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(role=constants.USER_ROLE_ADMIN)


class StaffManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            role__in=[constants.USER_ROLE_ADMIN, constants.USER_ROLE_STAFF]
        )


class DriverManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(role=constants.USER_ROLE_DRIVER)


class EscortManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(role=constants.USER_ROLE_ESCORT)


class CustomerManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(role=constants.USER_ROLE_CUSTOMER)


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('Users must have an username')

        user = self.model(
            username=username,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('role', constants.USER_ROLE_ADMIN)

        return self.create_user(
            username,
            password=password,
            **extra_fields
        )


class User(AbstractBaseUser):

    username = models.CharField(
        max_length=100,
        unique=True
    )

    email = models.EmailField(
        unique=True,
        null=True,
        blank=True
    )

    phone_number = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        validators=[validate_phone_number]
    )

    name = models.CharField(
        max_length=10,
        null=True,
        blank=True
    )

    date_joined = models.DateTimeField(
        auto_now_add=True
    )

    last_seen = models.DateTimeField(
        auto_now=True
    )

    is_active = models.BooleanField(
        default=True
    )

    role = models.CharField(
        max_length=1,
        choices=constants.USER_ROLE,
        default=constants.USER_ROLE_STAFF
    )

    objects = UserManager()
    admins = AdminManager()
    staffs = StaffManager()
    drivers = DriverManager()
    escorts = EscortManager()
    customers = CustomerManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def has_perm(self, perm, obj=None):
        if self.is_active and self.role == constants.USER_ROLE_ADMIN:
            return True

        return False

    def has_module_perms(self, app_label):
        if self.is_active and self.role == constants.USER_ROLE_ADMIN:
            return True

        return False

    @property
    def is_staff(self):
        return self.role in \
            [constants.USER_ROLE_ADMIN, constants.USER_ROLE_STAFF]
