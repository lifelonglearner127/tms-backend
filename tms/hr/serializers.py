from django.shortcuts import get_object_or_404
from rest_framework import serializers

from . import models as m
from ..account.models import UserPermission
from ..core import constants as c

# serializers
from ..account.serializers import (
    ShortUserSerializer, MainUserSerializer, UserSerializer,
    DriverAppUserSerializer
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

    class Meta:
        model = m.StaffProfile
        fields = (
            'id', 'name'
        )


class DriverAppStaffProfileSerializer(serializers.ModelSerializer):

    department = ShortDepartmentSerializer(read_only=True)
    position = ShortPositionSerializer(read_only=True)
    user = DriverAppUserSerializer(read_only=True)

    class Meta:
        model = m.StaffProfile
        fields = (
            'id', 'user', 'department', 'position'
        )


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

        # check user role
        user_data['role'] = user_data['role']['value']

        if user_data['role'] in [c.USER_ROLE_DRIVER, c.USER_ROLE_ESCORT]:
            driver_license_data = self.context.get('driver_license', None)
            if driver_license_data is None:
                raise serializers.ValidationError({
                    'license': 'Driver license data is missing'
                })

        permission = None
        if user_data['role'] == c.USER_ROLE_STAFF:
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
        if user_data['role'] in [c.USER_ROLE_DRIVER, c.USER_ROLE_ESCORT]:
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

        user_data['role'] = user_data['role']['value']
        if user_data['role'] in [c.USER_ROLE_DRIVER, c.USER_ROLE_ESCORT]:
            driver_license_data = self.context.get('driver_license', None)
            if driver_license_data is None:
                raise serializers.ValidationError({
                    'license': 'Driver License data is missing'
                })

        password = user_data.pop('password', None)
        if password is not None:
            instance.user.set_password(password)

        permission = None
        if user_data['role'] == c.USER_ROLE_STAFF:
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

        if user_data['role'] in [c.USER_ROLE_DRIVER, c.USER_ROLE_ESCORT]:
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


class ShortCustomerProfileSerializer(serializers.ModelSerializer):

    user_id = serializers.CharField(source='user.id')

    class Meta:
        model = m.CustomerProfile
        fields = (
            'id', 'user_id', 'name', 'contact', 'mobile'
        )


class CustomerProfileSerializer(serializers.ModelSerializer):

    user = MainUserSerializer(read_only=True)
    associated_with = ShortUserSerializer(read_only=True)

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

        user_data.setdefault('role', c.USER_ROLE_CUSTOMER)
        user = m.User.objects.create_user(**user_data)
        customer = m.CustomerProfile.objects.create(
            user=user,
            associated_with=associated_with,
            **validated_data
        )

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
        return instance
