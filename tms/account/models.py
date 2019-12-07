from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager

from . import managers
from ..core import constants as c
from ..core.validations import validate_mobile, validate_username


class UserManager(BaseUserManager):
    """
    Default User Model Manager
    """
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
        extra_fields.setdefault('user_type', c.USER_TYPE_ADMIN)

        user = self.create_user(
            username,
            password=password,
            **extra_fields
        )

        return user


class UserPermission(models.Model):

    name = models.CharField(
        max_length=100
    )

    permissions = models.ManyToManyField(
        'Permission'
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

    def has_permission(self, page, action):
        return self.permissions.filter(page=page, action=action).exists()


class Permission(models.Model):

    page = models.CharField(
        max_length=100
    )

    action = models.CharField(
        max_length=100
    )

    def __str__(self):
        return '{} permission on {} page'.format(self.action, self.page)


class User(AbstractBaseUser):
    """
    User model
    """
    username = models.CharField(
        max_length=100,
        unique=True,
        validators=[validate_username]
    )

    email = models.EmailField(
        unique=True,
        null=True,
        blank=True
    )

    mobile = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        validators=[validate_mobile]
    )

    device_token = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    channel_name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    name = models.CharField(
        max_length=100,
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

    user_type = models.CharField(
        max_length=1,
        choices=c.USER_TYPE,
        default=c.USER_TYPE_STAFF
    )

    permission = models.ForeignKey(
        UserPermission,
        on_delete=models.SET_NULL,
        null=True
    )

    @property
    def is_staff(self):
        return self.user_type in \
            [c.USER_TYPE_ADMIN, c.USER_TYPE_STAFF]

    @property
    def driverlicense_number(self):
        number = ""
        if self.profile:
            if self.profile.driver_license and self.profile.driver_license.first():
                number = self.profile.driver_license.first().number

        return number

    objects = UserManager()
    admins = managers.AdminUserManager()
    staffs = managers.StaffUserManager()
    drivers = managers.DriverUserManager()
    escorts = managers.EscortUserManager()
    wheels = managers.WheelUserManager()
    customers = managers.CustomerUserManager()
    securityofficers = managers.SecurityOfficerUserManager()
    companymembers = managers.CompanyMemberUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        if self.is_active and self.user_type == c.USER_TYPE_ADMIN:
            return True

        return False

    def has_module_perms(self, app_label):
        if self.is_active and self.user_type == c.USER_TYPE_ADMIN:
            return True

        return False
