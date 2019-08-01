from rest_framework import serializers

# models
from . import models as m

# serializers
from ..account.serializers import ShortUserSerializer


class CompanyContentSerializer(serializers.ModelSerializer):

    author = ShortUserSerializer(read_only=True)
    published_on = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    updated = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )

    class Meta:
        model = m.CompanyContent
        fields = '__all__'

    def create(self, validated_data):
        author_data = self.context.get('author', None)
        if author_data is None:
            raise serializers.ValidationError({
                'author': 'Author data is missing'
            })

        try:
            author = m.User.staffs.get(id=author_data.get('id'))
        except m.User.DoesNotExists:
            raise serializers.ValidationError({
                'author': 'Such user does not exits'
            })

        return self.Meta.model.objects.create(
            author=author,
            **validated_data
        )

    def update(self, instance, validated_data):
        author_data = self.context.get('author', None)
        if author_data is None:
            raise serializers.ValidationError({
                'author': 'Author data is missing'
            })

        try:
            author = m.User.staffs.get(id=author_data.get('id'))
        except m.User.DoesNotExists:
            raise serializers.ValidationError({
                'author': 'Such user does not exits'
            })

        instance.author = author
        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


class CompanyPolicySerializer(CompanyContentSerializer):

    class Meta(CompanyContentSerializer.Meta):
        model = m.CompanyPolicy


class SecurityKnowledgeSerializer(CompanyContentSerializer):

    class Meta(CompanyContentSerializer.Meta):
        model = m.SecurityKnowledge
