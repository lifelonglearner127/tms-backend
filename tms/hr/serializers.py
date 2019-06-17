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
