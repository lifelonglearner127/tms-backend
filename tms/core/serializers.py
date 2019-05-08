from rest_framework import serializers


class ChoiceSerializer(serializers.Serializer):
    """
    Used for serializing backend constant choices
    """
    value = serializers.CharField()
    text = serializers.CharField()
