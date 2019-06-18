from rest_framework import serializers

from . import models as m
from ..account.serializers import ShortStaffProfileSerializer


class RestRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.RestRequest
        fields = '__all__'


class RestRequestDataViewSerializer(serializers.ModelSerializer):

    staff = ShortStaffProfileSerializer()

    class Meta:
        model = m.RestRequest
        fields = '__all__'


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
