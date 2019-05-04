from rest_framework import serializers
from .models import User


class ShortUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id', 'name'
        )


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id', 'username', 'role'
        )
