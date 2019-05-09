from rest_framework import serializers

from . import models as m
from ..core import constants


class ShortUserSerializer(serializers.ModelSerializer):
    """
    Serializer for short data of User
    """
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
    """
    Serializer for auth data of user
    """
    class Meta:
        model = m.User
        fields = (
            'id', 'username', 'role'
        )


class MainUserSerializer(serializers.ModelSerializer):
    """
    Serializer for User's main data
    """
    class Meta:
        model = m.User
        fields = (
            'id', 'username', 'mobile', 'name', 'role', 'password'
        )


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User
    """
    class Meta:
        model = m.User
        fields = '__all__'


class StaffProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for StaffProfile
    """
    user = MainUserSerializer(read_only=True)

    class Meta:
        model = m.StaffProfile
        fields = '__all__'

    def create(self, validated_data):
        # get user data and create
        user_data = self.context.get('user', None)
        if user_data is None:
            raise serializers.ValidationError(
                'User data is not provided'
            )
        user = m.User.objects.create_user(**user_data)
        profile = m.StaffProfile.objects.create(
            user=user,
            **validated_data
        )
        return profile

    def update(self, instance, validated_data):
        user_data = self.context.get('user', None)
        if user_data is None:
            raise serializers.ValidationError(
                'User data is not provided'
            )
        password = user_data.pop('password', None)
        if password is not None:
            instance.user.set_password(password)

        for (key, value) in user_data.items():
            setattr(instance.user, key, value)
        instance.user.save()

        for (key, value) in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        return instance


class CustomerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Customer
    """
    user = MainUserSerializer(read_only=True)
    associated = ShortUserSerializer(read_only=True)

    class Meta:
        model = m.CustomerProfile
        fields = '__all__'

    def create(self, validated_data):
        # get user data and create one
        user_data = self.context.get('user', None)
        if user_data is None:
            raise serializers.ValidationError(
                'User data is not provided'
            )
        user_data.setdefault('role', constants.USER_ROLE_CUSTOMER)
        user = m.User.objects.create_user(**user_data)

        # get associated data
        associated_data = self.context.get('associated', None)
        if associated_data is None:
            raise serializers.ValidationError(
                'Associated data is not provided'
            )

        associated_id = associated_data.get('id', None)
        try:
            associated = m.User.objects.get(pk=associated_id)
        except m.User.objects.DoesNotExist:
            raise serializers.ValidationError(
                'Such associated user does not exist'
            )

        return m.CustomerProfile.objects.create(
            user=user,
            associated=associated,
            **validated_data
        )

    def update(self, instance, validated_data):
        # get user data and update
        user_data = self.context.get('user', None)
        if user_data is None:
            raise serializers.ValidationError(
                'User data is not provided'
            )
        user = instance.user
        user.username = user_data.get('username', user.username)
        user.mobile = user_data.get('mobile', user.mobile)
        user.name = user_data.get('name', user.name)
        user.set_password(user_data.get('password', user.password))
        user.save()

        # get associated data
        associated_data = self.context.get('associated', None)
        if associated_data is None:
            raise serializers.ValidationError(
                'Associated data is not provided'
            )

        associated_id = associated_data.get('id', None)
        try:
            associated = m.User.objects.get(pk=associated_id)
            instance.associated = associated
        except m.User.objects.DoesNotExist:
            raise serializers.ValidationError(
                'Such associated user does not exist'
            )

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


class StaffDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for StaffDocument
    """
    class Meta:
        model = m.StaffDocument
        fields = '__all__'
