from django.shortcuts import get_object_or_404
from rest_framework import serializers
from ..core import constants
from .models import User, CompanyStaffProfile, CustomerProfile


class ShortUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id', 'name'
        )


class AuthSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id', 'username', 'role'
        )


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


class ShortCompanyStaffSerializer(serializers.ModelSerializer):

    value = serializers.CharField(source='id')
    text = serializers.CharField(source='user.username')

    class Meta:
        model = CompanyStaffProfile
        fields = (
            'value', 'text'
        )


class CompanyStaffSerializer(serializers.ModelSerializer):

    user = UserSerializer()

    class Meta:
        model = CompanyStaffProfile
        fields = (
            'user', 'birthday', 'spouse_name', 'spouse_number'
        )

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        company_staff = CustomerProfile.objects.create(
            user=user,
            **validated_data
        )
        return company_staff


class CustomerSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)
    associated = ShortCompanyStaffSerializer(read_only=True)

    class Meta:
        model = CustomerProfile
        fields = '__all__'

    def create(self, validated_data):
        user_context = self.context.get('user')
        associated_id = self.context.get('associated')
        user_data = {
            'username': user_context.get('username'),
            'password': user_context.get('password'),
            'mobile': user_context.get('mobile'),
            'name': user_context.get('name'),
            'role': constants.USER_ROLE_CUSTOMER
        }
        user = User.objects.create_user(**user_data)
        associated = get_object_or_404(CompanyStaffProfile, pk=associated_id)

        customer = CustomerProfile.objects.create(
            user=user,
            associated=associated,
            **validated_data
        )
        return customer

    def update(self, instance, validated_data):
        user = instance.user
        user_context = self.context.get('user')

        user.username = user_context.get('username', user.username)
        user.mobile = user_context.get('mobile', user.mobile)
        user.name = user_context.get('name', user.name)
        user.set_password(user_context.get('password', user.password))
        user.save()

        instance.good = validated_data.get('good', instance.good)
        instance.payment_unit = validated_data.get(
            'payment_unit', instance.payment_unit
        )
        instance.address = validated_data.get('address', instance.address)
        associated_id = self.context.get('associated')
        associated = get_object_or_404(CompanyStaffProfile, pk=associated_id)
        instance.associated = associated
        instance.save()
        return instance
