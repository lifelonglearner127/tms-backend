from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager

from . import managers
from ..core import constants as c
from ..core.models import BasicContactModel
from ..core.validations import validate_mobile
from ..info.models import Product


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
        extra_fields.setdefault('role', c.USER_ROLE_ADMIN)

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

    role = models.CharField(
        max_length=1,
        choices=c.USER_ROLE,
        default=c.USER_ROLE_STAFF
    )

    @property
    def is_staff(self):
        return self.role in \
            [c.USER_ROLE_ADMIN, c.USER_ROLE_STAFF]

    objects = UserManager()
    admins = managers.UserAdminManager()
    staffs = managers.UserStaffManager()
    drivers = managers.UserDriverManager()
    escorts = managers.UserEscortManager()
    customers = managers.UserCustomerManager()
    companymembers = managers.UserCompanyMemberManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        if self.is_active and self.role == c.USER_ROLE_ADMIN:
            return True

        return False

    def has_module_perms(self, app_label):
        if self.is_active and self.role == c.USER_ROLE_ADMIN:
            return True

        return False


class BaseStaffProfile(models.Model):
    """
    Company Staff Profile Model
    """

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

    class Meta:
        abstract = True


class StaffProfile(BaseStaffProfile):

    user = models.OneToOneField(
        User,
        related_name='staff_profile',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return '{}-{}\'s profile'.format(
            self.user.role, self.user.username
        )


class DriverProfile(BaseStaffProfile):

    user = models.OneToOneField(
        User,
        related_name='driver_profile',
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=1,
        choices=c.DRIVER_STATUS,
        default=c.DRIVER_STATUS_AVAILABLE
    )

    objects = models.Manager()
    availables = managers.AvailableDriverManager()
    inworks = managers.InWorkDriverManager()

    def __str__(self):
        return '{}-{}\'s profile'.format(
            self.user.role, self.user.username
        )


class EscortProfile(BaseStaffProfile):

    user = models.OneToOneField(
        User,
        related_name='escort_profile',
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=1,
        choices=c.DRIVER_STATUS,
        default=c.DRIVER_STATUS_AVAILABLE
    )

    objects = models.Manager()
    availables = managers.AvailableDriverManager()
    inworks = managers.InWorkDriverManager()

    def __str__(self):
        return '{}-{}\'s profile'.format(
            self.user.role, self.user.username
        )


class CustomerProfile(BasicContactModel):
    """
    Customer Profile Model
    """
    user = models.OneToOneField(
        User,
        related_name='customer_profile',
        on_delete=models.CASCADE
    )

    products = models.ManyToManyField(
        Product
    )

    product_characteristics = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    payment_method = models.CharField(
        max_length=1,
        choices=c.PAYMENT_METHOD,
        default=c.PAYMENT_METHOD_TON
    )

    associated_with = models.ForeignKey(
        StaffProfile,
        related_name='customers',
        on_delete=models.SET_NULL,
        null=True
    )

    customer_request = models.TextField(
        null=True,
        blank=True
    )

    def __str__(self):
        return '{}\'s profile'.format(self.user.username)

    class Meta:
        ordering = ['-updated']


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
        choices=c.USER_DOCUMENT_TYPE,
        default=c.USER_DOCUMENT_TYPE_D1
    )

    expires_on = models.DateField()

    description = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    def __str__(self):
        return '{}\'s {} document' .format(self.staff.user.username, self.name)
