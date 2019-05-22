from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager

from . import managers
from ..core import constants
from ..core.validations import validate_mobile


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
        extra_fields.setdefault('role', constants.USER_ROLE_ADMIN)

        user = self.create_user(
            username,
            password=password,
            **extra_fields
        )

        StaffProfile.objects.create(user=user)
        return user


class User(AbstractBaseUser):
    """
    User model
    """
    username = models.CharField(
        max_length=100,
        unique=True
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
        unique=True,
        null=True,
        blank=True
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

    @property
    def is_staff(self):
        return self.role in \
            [constants.USER_ROLE_ADMIN, constants.USER_ROLE_STAFF]

    objects = UserManager()
    admins = managers.AdminManager()
    staffs = managers.StaffManager()
    drivers = managers.DriverManager()
    escorts = managers.EscortManager()
    customers = managers.CustomerManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        if self.is_active and self.role == constants.USER_ROLE_ADMIN:
            return True

        return False

    def has_module_perms(self, app_label):
        if self.is_active and self.role == constants.USER_ROLE_ADMIN:
            return True

        return False


class StaffProfile(models.Model):
    """
    Company Staff Profile Model
    """
    user = models.OneToOneField(
        User,
        related_name='staff_profile',
        on_delete=models.CASCADE
    )

    id_card = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    birthday = models.DateField(
        null=True,
        blank=True
    )

    emergency_number = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    spouse_name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    spouse_number = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    parent_name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    parent_number = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    address = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    objects = models.Manager()
    drivers = managers.StaffDriverManager()
    escorts = managers.StaffEscortManager()

    def __str__(self):
        return '{}\'s profile'.format(self.user.username)


class CustomerProfile(models.Model):
    """
    Customer Profile Model
    """
    user = models.OneToOneField(
        User,
        related_name='customer_profile',
        on_delete=models.CASCADE
    )

    good = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    payment_unit = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    associated_with = models.ForeignKey(
        StaffProfile,
        related_name='in_charges',
        on_delete=models.SET_NULL,
        null=True
    )

    address = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    def __str__(self):
        return '{}\'s profile'.format(self.user.username)


class StaffDocument(models.Model):
    """
    Staff Document Model
    """
    staff = models.ForeignKey(
        StaffProfile,
        related_name='documents',
        on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=100
    )

    no = models.CharField(
        max_length=100
    )

    document_type = models.CharField(
        max_length=1,
        choices=constants.USER_DOCUMENT_TYPE,
        default=constants.USER_DOCUMENT_TYPE_D1
    )

    expires_on = models.DateField()

    description = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    def __str__(self):
        return '{}\'s {} document' .format(self.staff.user.username, self.name)
