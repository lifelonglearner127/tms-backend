from rest_framework import serializers
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

    class Meta:
        model = CustomerProfile
        fields = (
            'id', 'user', 'good', 'payment_unit', 'associated'
        )

    def create(self, validated_data):
        context = self.context.get('user')
        user_data = {
            'username': context.get('username'),
            'mobile': context.get('mobile'),
            'name': context.get('name')
        }
        user = User.objects.create_user(**user_data)
        customer = CustomerProfile.objects.create(
            user=user,
            **validated_data
        )
        return customer

    def update(self, instance, validated_data):
        user = instance.user
        context = self.context.get('user')

        user.username = context.get('username', user.username)
        user.mobile = context.get('mobile', user.mobile)
        user.name = context.get('name', user.name)
        user.save()

        instance.good = validated_data.get('good', instance.good)
        instance.payment_unit = validated_data.get(
            'payment_unit', instance.payment_unit
        )
        instance.associated = validated_data.get(
            'associated', instance.associated
        )
        instance.save()
        return instance
