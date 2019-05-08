from rest_framework import serializers

from .models import Job
from ..order.serializers import OrderProductDeliverSerializer
from ..account.serializers import ShortUserSerializer


class JobSerializer(serializers.ModelSerializer):

    mission = OrderProductDeliverSerializer(read_only=True)
    driver = ShortUserSerializer(read_only=True)
    escort = ShortUserSerializer(read_only=True)

    class Meta:
        model = Job
        fields = '__all__'
