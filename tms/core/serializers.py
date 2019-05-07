from rest_framework import serializers


class ChoiceSerializer(serializers.Serializer):

    value = serializers.CharField()
    text = serializers.CharField()
