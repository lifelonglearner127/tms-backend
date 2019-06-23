from rest_framework import serializers

from . import models as m
from ..core import constants as c
from ..core.serializers import TMSChoiceField
from ..account.models import User
from ..account.serializers import (
    ShortUserSerializer, MainUserSerializer, UserSerializer
)
from ..info.models import Product
from ..info.serializers import ShortProductSerializer


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


class RoleManagementDataViewSerializer(serializers.ModelSerializer):

    department = ShortDepartmentSerializer()
    position = ShortPositionSerializer()

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


class StaffProfileSerializer(serializers.ModelSerializer):

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

        # check user role
        user_data['role'] = user_data['role']['value']
        user = m.User.objects.create_user(**user_data)

        driver_license = self.context.get('driver_license', None)
        if driver_license is not None:
            driver_license = m.DriverLicense.objects.create(
                **driver_license
            )

        profile = m.StaffProfile.objects.create(
            user=user,
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

        password = user_data.pop('password', None)
        if password is not None:
            instance.user.set_password(password)

        user_data['role'] = user_data['role']['value']
        for (key, value) in user_data.items():
            setattr(instance.user, key, value)
        instance.user.save()

        for (key, value) in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        return instance


class StaffProfileDataViewSerializer(serializers.ModelSerializer):

    user = UserSerializer()
    department = ShortDepartmentSerializer()
    position = ShortPositionSerializer()
    driver_license = DriverLicenseSerializer()

    class Meta:
        model = m.StaffProfile
        fields = '__all__'


class ShortCustomerProfileSerializer(serializers.ModelSerializer):

    user_id = serializers.CharField(source='user.id')
    name = serializers.CharField(source='user.name')
    mobile = serializers.CharField(source='user.mobile')

    class Meta:
        model = m.CustomerProfile
        fields = (
            'id', 'name', 'mobile'
        )


class CustomerProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.CustomerProfile
        fields = '__all__'
        read_only_fields = ('user', 'products')

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

        products_data = self.context.get('products', None)
        if products_data is None:
            raise serializers.ValidationError({
                'product': 'Product data is not provided'
            })

        user = m.User.objects.create_user(**user_data)
        customer = m.CustomerProfile.objects.create(
            user=user,
            **validated_data
        )

        for product_data in products_data:
            product_id = product_data.get('id', None)
            try:
                product = Product.objects.get(pk=product_id)
                customer.products.add(product)
            except Product.DoesNotExist:
                pass

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

        products_data = self.context.get('products', None)
        if products_data is None:
            raise serializers.ValidationError({
                'product': 'Product data is not provided'
            })

        instance.products.clear()
        for product_data in products_data:
            product_id = product_data.get('id', None)
            try:
                product = Product.objects.get(pk=product_id)
                instance.products.add(product)
            except Product.DoesNotExist:
                pass

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


class CustomerProfileDataViewSerializer(serializers.ModelSerializer):

    user = MainUserSerializer()
    products = ShortProductSerializer(many=True)
    associated_with = ShortStaffProfileSerializer()
    payment_method = TMSChoiceField(choices=c.PAYMENT_METHOD)

    class Meta:
        model = m.CustomerProfile
        fields = '__all__'


class RestRequestSerializer(serializers.ModelSerializer):

    user = ShortUserSerializer(read_only=True)
    category = TMSChoiceField(choices=c.REST_REQUEST_CATEGORY)

    class Meta:
        model = m.RestRequest
        fields = '__all__'

    def create(self, validated_data):
        try:
            user_id = self.context.pop('user')
            user = User.companymembers.get(pk=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'user': 'User does not exist'
            })

        return m.RestRequest.objects.create(
            user=user,
            **validated_data
        )

    def update(self, instance, validated_data):
        user_id = self.context.pop('user')
        try:
            user_id = self.context.pop('user')
            user = User.companymembers.get(pk=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'user': 'User does not exist'
            })

        for (key, value) in validated_data.items():
            setattr(instance, key, value)
        instance.user = user
        instance.save()
        return instance

    def validate(self, data):
        from_date = data.get('from_date', None)
        to_date = data.get('to_date', None)

        if from_date > to_date:
            raise serializers.ValidationError({
                'to_date': 'Error'
            })

        return data
