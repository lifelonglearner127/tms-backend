from django.shortcuts import get_object_or_404
from rest_framework import serializers

from . import models as m
from ..account.models import UserPermission
from ..vehicle.models import VehicleDriverDailyBind
from ..core import constants as c

# serializers
from ..account.serializers import (
    ShortUserSerializer, MainUserSerializer, UserSerializer,
    DriverAppUserSerializer, CustomerAppUserSerializer
)


class ShortDepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Department
        fields = (
            'id', 'name'
        )


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Department
        fields = '__all__'


class ShortPositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Position
        fields = (
            'id', 'name'
        )


class PositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Position
        fields = '__all__'


class RoleManagementSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.RoleManagement
        fields = '__all__'


class DriverLicenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.DriverLicense
        fields = '__all__'


class ShortStaffProfileSerializer(serializers.ModelSerializer):

    name = serializers.CharField(source='user.name')
    mobile = serializers.CharField(source='user.mobile')
    license_expiration = serializers.SerializerMethodField()
    bind_vehicle = serializers.SerializerMethodField()
    driverlicense_number = serializers.SerializerMethodField()

    def get_bind_vehicle(self, instance):
        bind = VehicleDriverDailyBind.objects.filter(driver=instance.user, get_off=None).first()
        if bind is not None:
            return {
                'id': bind.vehicle.id,
                'plate_num': bind.vehicle.plate_num
            }
        else:
            return None

    class Meta:
        model = m.StaffProfile
        fields = (
            'id',
            'name',
            'mobile',
            'emergency_number',
            'id_card',
            'status',
            'license_expiration',
            'bind_vehicle',
            'driving_duration',
            # 'next_job_customer',
            'driverlicense_number'
        )

    def get_license_expiration(self, instance):
        expiration = ""
        if instance.driver_license:
            expiration = instance.driver_license.expires_on

        return expiration

    def get_driverlicense_number(self, instance):
        number = ""
        if instance.driver_license:
            number = instance.driver_license.number

        return number


class DriverAppStaffProfileSerializer(serializers.ModelSerializer):

    department = ShortDepartmentSerializer(read_only=True)
    position = ShortPositionSerializer(read_only=True)
    user = DriverAppUserSerializer(read_only=True)
    bind_vehicle = serializers.SerializerMethodField()

    class Meta:
        model = m.StaffProfile
        fields = (
            'id', 'user', 'department', 'position', 'bind_vehicle'
        )

    def get_bind_vehicle(self, instance):
        bind = VehicleDriverDailyBind.objects.filter(driver=instance.user, get_off=None).first()
        if bind is not None:
            return {
                'id': bind.vehicle.id,
                'plate_num': bind.vehicle.plate_num
            }
        else:
            return None


class StaffProfileSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)
    driver_license = DriverLicenseSerializer(read_only=True)
    department = ShortDepartmentSerializer(read_only=True)
    position = ShortPositionSerializer(read_only=True)

    class Meta:
        model = m.StaffProfile
        fields = '__all__'
        read_only_fields = ('user', 'driver_license')

    def create(self, validated_data):
        # get user data and create
        user_data = self.context.get('user', None)
        if user_data is None:
            raise serializers.ValidationError({
                'user': 'User data is not provided'
            })

        # check if username and mobile exists already
        if m.User.objects.filter(username=user_data['username']).exists():
            raise serializers.ValidationError({
                'username': 'Such user already exists'
            })

        if m.User.objects.filter(mobile=user_data['mobile']).exists():
            raise serializers.ValidationError({
                'mobile': 'Such mobile already exisits'
            })

        # check user user_type
        user_data['user_type'] = user_data['user_type']['value']

        if user_data['user_type'] in [c.USER_TYPE_DRIVER, c.USER_TYPE_ESCORT]:
            driver_license_data = self.context.get('driver_license', None)
            if driver_license_data is None:
                raise serializers.ValidationError({
                    'license': 'Driver license data is missing'
                })

        permission = None
        if user_data['user_type'] == c.USER_TYPE_STAFF:
            permission_data = user_data.pop('permission')
            permission = get_object_or_404(
                UserPermission, id=permission_data.get('id', None)
            )

        user = m.User.objects.create_user(permission=permission, **user_data)

        department_data = self.context.get('department', None)
        department = get_object_or_404(
            m.Department,
            id=department_data.get('id', None)
        )

        position_data = self.context.get('position', None)
        position = get_object_or_404(
            m.Position,
            id=position_data.get('id', None)
        )

        driver_license = None
        if user_data['user_type'] in [c.USER_TYPE_DRIVER, c.USER_TYPE_ESCORT]:
            driver_license = m.DriverLicense.objects.create(
                **driver_license_data
            )

        profile = m.StaffProfile.objects.create(
            user=user,
            department=department,
            position=position,
            driver_license=driver_license,
            **validated_data
        )
        return profile

    def update(self, instance, validated_data):
        user_data = self.context.get('user', None)
        if user_data is None:
            raise serializers.ValidationError({
                'user': 'User data is not provided'
            })

        # check if username and mobile exists already
        if m.User.objects.exclude(pk=instance.user.id).filter(
            username=user_data['username']
        ).exists():
            raise serializers.ValidationError({
                'username': 'Such user already exists'
            })

        if m.User.objects.exclude(pk=instance.user.id).filter(
            mobile=user_data['mobile']
        ).exists():
            raise serializers.ValidationError({
                'mobile': 'Such mobile already exisits'
            })

        user_data['user_type'] = user_data['user_type']['value']
        if user_data['user_type'] in [c.USER_TYPE_DRIVER, c.USER_TYPE_ESCORT]:
            driver_license_data = self.context.get('driver_license', None)
            if driver_license_data is None:
                raise serializers.ValidationError({
                    'license': 'Driver License data is missing'
                })

        password = user_data.pop('password', None)
        if password is not None:
            instance.user.set_password(password)

        permission = None
        if user_data['user_type'] == c.USER_TYPE_STAFF:
            permission_data = user_data.pop('permission')
            permission = get_object_or_404(
                UserPermission, id=permission_data.get('id', None)
            )
            instance.user.permission = permission

        for (key, value) in user_data.items():
            setattr(instance.user, key, value)
        instance.user.save()

        department_data = self.context.get('department', None)
        department = get_object_or_404(
            m.Department,
            id=department_data.get('id', None)
        )

        position_data = self.context.get('position', None)
        position = get_object_or_404(
            m.Position,
            id=position_data.get('id', None)
        )

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        if user_data['user_type'] in [c.USER_TYPE_DRIVER, c.USER_TYPE_ESCORT]:
            if instance.driver_license is None:
                driver_license = m.DriverLicense.objects.create(
                    **driver_license_data
                )
                instance.driver_license = driver_license
            else:
                for (key, value) in driver_license_data.items():
                    setattr(instance.driver_license, key, value)

                instance.driver_license.save()

        instance.department = department
        instance.position = position
        instance.save()

        return instance

    def to_internal_value(self, data):
        """
        Exclude date, datetimefield if its string is empty
        """
        for key, value in self.fields.items():
            if isinstance(value, serializers.DateField) and data[key] == '':
                data.pop(key)

        ret = super().to_internal_value(data)
        return ret


class CustomerContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.CustomerContact
        fields = '__all__'


class ShortCustomerProfileSerializer(serializers.ModelSerializer):

    user_id = serializers.CharField(source='user.id')
    primary_contact = serializers.SerializerMethodField()

    class Meta:
        model = m.CustomerProfile
        fields = (
            'id', 'user_id', 'name', 'primary_contact'
        )

    def get_primary_contact(self, instance):
        return CustomerContactSerializer(instance.contacts.first()).data


class CustomerProfileSerializer(serializers.ModelSerializer):

    user = MainUserSerializer(read_only=True)
    associated_with = ShortUserSerializer(read_only=True)
    contacts = CustomerContactSerializer(many=True, read_only=True)
    primary_contact = serializers.SerializerMethodField()

    class Meta:
        model = m.CustomerProfile
        fields = '__all__'
        # read_only_fields = ('user', 'products')
        read_only_fields = ('user', )

    def create(self, validated_data):
        user_data = self.context.get('user', None)
        if user_data is None:
            raise serializers.ValidationError({
                'user': 'User data is not provided'
            })

        # check if username and mobile exists already
        if m.User.objects.filter(username=user_data['username']).exists():
            raise serializers.ValidationError({
                'username': 'Such user already exists'
            })

        associated_with = self.context.get('associated_with', None)
        if associated_with is None:
            raise serializers.ValidationError({
                'associated_with': 'Associated data are missing'
            })

        associated_id = associated_with.get('id', None)
        try:
            associated_with = m.User.objects.get(id=associated_id)
        except m.User.objects.DoesNotExist:
            raise serializers.ValidationError({
                'associated_with': 'Such user does not exist'
            })

        user_data.setdefault('user_type', c.USER_TYPE_CUSTOMER)
        user = m.User.objects.create_user(**user_data)
        customer = m.CustomerProfile.objects.create(
            user=user,
            associated_with=associated_with,
            **validated_data
        )

        for contact in self.context.get('contacts', []):
            customer_contact = m.CustomerContact.objects.create(**contact)
            customer.contacts.add(customer_contact)

        return customer

    def update(self, instance, validated_data):
        # get user data and update
        user_data = self.context.get('user', None)
        if user_data is None:
            raise serializers.ValidationError({
                'user': 'User Data is not provided'
            })
        user = instance.user

        # check if user id exists already
        if m.User.objects.exclude(pk=user.id).filter(
            username=user_data['username']
        ).exists():
            raise serializers.ValidationError({
                'username': 'Such user already exists'
            })

        user.username = user_data.get('username', user.username)
        user.set_password(user_data.get('password', user.password))
        user.save()

        associated_with = self.context.get('associated_with', None)
        if associated_with is None:
            raise serializers.ValidationError({
                'associated_with': 'Associated data are missing'
            })

        associated_id = associated_with.get('id', None)
        try:
            associated_with = m.User.objects.get(id=associated_id)
        except m.User.objects.DoesNotExist:
            raise serializers.ValidationError({
                'associated_with': 'Such user does not exist'
            })

        instance.associated_with = associated_with
        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        instance.contacts.clear()
        for contact in self.context.get('contacts', []):
            customer_contact = m.CustomerContact.objects.create(
                contact=contact.get('contact', ''),
                mobile=contact.get('mobile', '')
            )
            instance.contacts.add(customer_contact)

        return instance

    def get_primary_contact(self, instance):
        return CustomerContactSerializer(instance.contacts.first()).data


class CustomerAppProfileSerializer(serializers.ModelSerializer):

    user = CustomerAppUserSerializer(read_only=True)

    class Meta:
        model = m.CustomerProfile
        fields = (
            'id', 'user', 'name', 'contact', 'mobile'
        )


# version 2
class DriverEscortStatusSerializer(serializers.Serializer):
    """
    Serializer for driver, escort status in arrange view
    """
    id = serializers.IntegerField()
    name = serializers.CharField()
    mobile = serializers.CharField()
    id_card = serializers.CharField()
    vehicle = serializers.CharField()
    duration = serializers.IntegerField()
    # current_progress = serializers.CharField()
