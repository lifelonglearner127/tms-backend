import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import serializers

from . import models as m
from . import utils
from ..core import constants as c


class PasswordField(serializers.CharField):

    def __init__(self, *args, **kwargs):
        if 'style' not in kwargs:
            kwargs['style'] = {'input_type': 'password'}
        else:
            kwargs['style']['input_type'] = 'password'
        super(PasswordField, self).__init__(*args, **kwargs)


class AuthSerializer(serializers.ModelSerializer):
    """
    Serializer for auth data of user
    """
    class Meta:
        model = m.User
        fields = (
            'id', 'username', 'role', 'name'
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret['name'] is None:
            ret['name'] = instance.username

        return ret


class ObtainJWTSerializer(serializers.Serializer):
    """
    Serializer class used to validate a username and password.

    'username' is identified by the custom UserModel.USERNAME_FIELD.

    Returns a JSON Web Token that can be used to authenticate later calls.
    """
    username = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'}
    )
    role = serializers.CharField()
    device_token = serializers.CharField(required=False)

    def validate(self, attrs):
        credentials = {
            'username': attrs.get('username'),
            'password': attrs.get('password'),
            'role': attrs.get('role')
        }

        if all(credentials.values()):
            credentials['device_token'] = attrs.get('device_token', None)
            user = authenticate(**credentials)

            if user:
                if not user.is_active:
                    msg = 'User account is disabled.'
                    raise serializers.ValidationError(msg)

                payload = utils.jwt_payload_handler(user)

                return {
                    'token': utils.jwt_encode_handler(payload),
                    'user': user
                }
            else:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg)
        else:
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg)


class VerificationBaseSerializer(serializers.Serializer):
    """
    Abstract serializer used for verifying and refreshing JWTs.
    """
    token = serializers.CharField()

    def validate(self, attrs):
        msg = 'Please define a validate method.'
        raise NotImplementedError(msg)

    def _check_payload(self, token):
        # Check payload valid (based off of JSONWebTokenAuthentication,
        # may want to refactor)
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except jwt.ExpiredSignature:
            msg = 'Signature has expired.'
            raise serializers.ValidationError(msg)
        except jwt.DecodeError:
            msg = 'Error decoding signature.'
            raise serializers.ValidationError(msg)

        return payload

    def _check_user(self, payload):
        username = payload.get('username')

        if not username:
            msg = 'Invalid payload.'
            raise serializers.ValidationError(msg)

        # Make sure user exists
        try:
            user = m.User.objects.get(username=username)
        except m.User.DoesNotExist:
            msg = "User doesn't exist."
            raise serializers.ValidationError(msg)

        if not user.is_active:
            msg = 'User account is disabled.'
            raise serializers.ValidationError(msg)

        return user


class VerifyJWTSerializer(VerificationBaseSerializer):
    """
    Check the veracity of an access token.
    """

    def validate(self, attrs):
        token = attrs['token']

        payload = self._check_payload(token=token)
        user = self._check_user(payload=payload)

        return {
            'token': token,
            'user': user
        }


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


class ShortStaffProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for short data of staff profile
    """
    name = serializers.CharField(source='user.name')

    class Meta:
        model = m.StaffProfile
        fields = (
            'id', 'name'
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret['name'] is None:
            ret['name'] = instance.user.username

        return ret


class OnlyStaffProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.StaffProfile
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


class ShortDriverProfileSerializer(serializers.ModelSerializer):

    name = serializers.CharField(source='user.name')

    class Meta:
        model = m.DriverProfile
        fields = (
            'id', 'name'
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret['name'] is None:
            ret['name'] = instance.user.username

        return ret


class OnlyDriverProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.DriverProfile
        fields = '__all__'


class DriverProfileSerializer(serializers.ModelSerializer):

    user = MainUserSerializer(read_only=True)

    class Meta:
        model = m.DriverProfile
        fields = '__all__'

    def create(self, validated_data):
        # get user data and create
        user_data = self.context.get('user', None)
        if user_data is None:
            raise serializers.ValidationError(
                'User data is not provided'
            )
        user = m.User.objects.create_user(**user_data)
        profile = m.DriverProfile.objects.create(
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


class ShortEscortProfileSerializer(serializers.ModelSerializer):

    name = serializers.CharField(source='user.name')

    class Meta:
        model = m.EscortProfile
        fields = (
            'id', 'name'
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret['name'] is None:
            ret['name'] = instance.user.username

        return ret


class OnlyEscortProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.EscortProfile
        fields = '__all__'


class EscortProfileSerializer(serializers.ModelSerializer):

    user = MainUserSerializer(read_only=True)

    class Meta:
        model = m.EscortProfile
        fields = '__all__'

    def create(self, validated_data):
        # get user data and create
        user_data = self.context.get('user', None)
        if user_data is None:
            raise serializers.ValidationError(
                'User data is not provided'
            )
        user = m.User.objects.create_user(**user_data)
        profile = m.EscortProfile.objects.create(
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


class ShortCustomerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for short data of customer profile
    """
    name = serializers.CharField(source='user.name')
    mobile = serializers.CharField(source='user.mobile')

    class Meta:
        model = m.CustomerProfile
        fields = (
            'id', 'name', 'mobile'
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret['name'] is None:
            ret['name'] = instance.user.username

        return ret


class CustomerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Customer
    """
    user = MainUserSerializer(read_only=True)
    associated_with = ShortStaffProfileSerializer(read_only=True)

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
        user_data.setdefault('role', c.USER_ROLE_CUSTOMER)

        # check if user id exists already
        user_validator = {}
        if m.User.objects.filter(username=user_data['username']).exists():
            user_validator['username'] = 'duplicate'

        if m.User.objects.filter(mobile=user_data['mobile']).exists():
            user_validator['mobile'] = 'duplicate'

        if user_validator:
            raise serializers.ValidationError(user_validator)

        user = m.User.objects.create_user(**user_data)

        # get associated data
        associated_data = self.context.get('associated_with', None)
        if associated_data is None:
            raise serializers.ValidationError(
                'Associated data is not provided'
            )

        associated_id = associated_data.get('id', None)
        try:
            associated = m.StaffProfile.objects.get(pk=associated_id)
        except m.StaffProfile.objects.DoesNotExist:
            raise serializers.ValidationError(
                'Such associated user does not exist'
            )

        return m.CustomerProfile.objects.create(
            user=user,
            associated_with=associated,
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

        # check if user id & mobile exists already
        user_validator = {}
        if m.User.objects.exclude(pk=user.id).filter(
            username=user_data['username']
        ).exists():
            user_validator['username'] = 'duplicate'

        if m.User.objects.exclude(pk=user.id).filter(
            mobile=user_data['mobile']
        ).exists():
            user_validator['mobile'] = 'duplicate'

        if user_validator:
            raise serializers.ValidationError(user_validator)

        user.username = user_data.get('username', user.username)
        user.mobile = user_data.get('mobile', user.mobile)
        user.name = user_data.get('name', user.name)
        user.set_password(user_data.get('password', user.password))
        user.save()

        # get associated data
        associated_data = self.context.get('associated_with', None)
        if associated_data is None:
            raise serializers.ValidationError(
                'Associated data is not provided'
            )

        associated_id = associated_data.get('id', None)
        try:
            associated_with = m.StaffProfile.objects.get(pk=associated_id)
            instance.associated_with = associated_with
        except m.StaffProfile.objects.DoesNotExist:
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


class CompanyMemberSerializer(serializers.ModelSerializer):

    profile = serializers.SerializerMethodField()
    role_name = serializers.CharField(
        source='get_role_display', read_only=True
    )

    class Meta:
        model = m.User
        fields = (
            'id', 'username', 'mobile', 'name', 'password', 'role_name',
            'role', 'profile'
        )

    def create(self, validated_data):
        # get user data and create
        profile_data = self.context.get('profile', None)
        if profile_data is None:
            raise serializers.ValidationError(
                'Profile data is not provided'
            )
        user = m.User.objects.create_user(**validated_data)
        if user.role == c.USER_ROLE_STAFF:
            m.StaffProfile.objects.create(
                user=user,
                **profile_data
            )
        elif user.role == c.USER_ROLE_DRIVER:
            m.DriverProfile.objects.create(
                user=user,
                **profile_data
            )
        elif user.role == c.USER_ROLE_ESCORT:
            m.EscortProfile.objects.create(
                user=user,
                **profile_data
            )

        return user

    def update(self, instance, validated_data):
        profile_data = self.context.get('profile', None)
        if profile_data is None:
            raise serializers.ValidationError(
                'Profile data is not provided'
            )
        password = validated_data.pop('password', None)
        if password is not None:
            instance.set_password(password)

        pre_role = instance.role
        for (key, value) in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        if pre_role == instance.role:
            if instance.role == c.USER_ROLE_STAFF:
                for (key, value) in profile_data.items():
                    setattr(instance.staff_profile, key, value)
                instance.staff_profile.save()
            elif instance.role == c.USER_ROLE_DRIVER:
                for (key, value) in profile_data.items():
                    setattr(instance.driver_profile, key, value)
                instance.driver_profile.save()
            elif instance.role == c.USER_ROLE_ESCORT:
                for (key, value) in profile_data.items():
                    setattr(instance.escort_profile, key, value)
                instance.escort_profile.save()
        else:
            if pre_role == c.USER_ROLE_STAFF:
                instance.staff_profile.delete()
            elif pre_role == c.USER_ROLE_DRIVER:
                instance.driver_profile.delete()
            elif pre_role == c.USER_ROLE_ESCORT:
                instance.escort_profile.delete()

            if instance.role == c.USER_ROLE_STAFF:
                m.StaffProfile.objects.create(
                    user=instance,
                    **profile_data
                )
            elif instance.role == c.USER_ROLE_DRIVER:
                m.DriverProfile.objects.create(
                    user=instance,
                    **profile_data
                )
            elif instance.role == c.USER_ROLE_ESCORT:
                m.EscortProfile.objects.create(
                    user=instance,
                    **profile_data
                )

        return instance

    def get_profile(self, user):
        if user.role == c.USER_ROLE_DRIVER:
            return OnlyDriverProfileSerializer(user.driver_profile).data
        elif user.role == c.USER_ROLE_ESCORT:
            return OnlyEscortProfileSerializer(user.escort_profile).data
        elif user.role == c.USER_ROLE_STAFF:
            return OnlyStaffProfileSerializer(user.staff_profile).data
