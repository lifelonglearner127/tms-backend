from django.shortcuts import get_object_or_404

from rest_framework import serializers

from . import models as m
from ..core import constants


class ShortUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.User
        fields = (
            'id', 'name', 'mobile'
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret['name'] is None:
            ret['name'] = instance.username

        return ret


class AuthSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.User
        fields = (
            'id', 'username', 'role'
        )


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.User
        fields = '__all__'


class StaffProfileSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)

    class Meta:
        model = m.StaffProfile
        fields = '__all__'

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = m.User.objects.create_user(**user_data)
        profile = m.StaffProfile.objects.create(
            user=user,
            **validated_data
        )
        return profile


class CustomerSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)
    associated = UserSerializer(read_only=True)

    class Meta:
        model = m.CustomerProfile
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
        user = m.User.objects.create_user(**user_data)
        associated = get_object_or_404(m.User, pk=associated_id)

        customer = m.CustomerProfile.objects.create(
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
        associated = get_object_or_404(m.CompanyStaffProfile, pk=associated_id)
        instance.associated = associated
        instance.save()
        return instance
