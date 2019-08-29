from rest_framework import serializers

from ..core import constants as c

# models
from . import models as m

# serializers
from ..core.serializers import TMSChoiceField
from ..account.serializers import ShortUserSerializer, ShortWheelUserWithDepartmentSerializer


class ShortCompanyPolicySerializer(serializers.ModelSerializer):

    policy_type = TMSChoiceField(c.COMPANY_POLICY_TYPE)
    published_on = serializers.DateTimeField(format='%Y-%m-%d', required=False)
    author = ShortUserSerializer(read_only=True)

    class Meta:
        model = m.CompanyPolicy
        exclude = (
            'is_published', 'content'
        )


class CompanyPolicySerializer(serializers.ModelSerializer):

    author = ShortUserSerializer(read_only=True)
    policy_type = TMSChoiceField(c.COMPANY_POLICY_TYPE)
    published_on = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    updated = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )

    class Meta:
        model = m.CompanyPolicy
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


class ShortQuestionSerializer(serializers.ModelSerializer):

    question_type = TMSChoiceField(choices=c.QUESTION_TYPE)
    created = serializers.DateTimeField(
        format='%Y-%m-%d', required=False
    )

    class Meta:
        model = m.Question
        fields = (
            'id', 'question_type', 'title', 'created'
        )


class QuestionSerializer(serializers.ModelSerializer):

    question_type = TMSChoiceField(choices=c.QUESTION_TYPE)
    created = serializers.DateTimeField(
        format='%Y-%m-%d', required=False
    )

    class Meta:
        model = m.Question
        fields = '__all__'


class ShortTestResult(serializers.ModelSerializer):

    class Meta:
        model = m.TestResult
        exclude = (
            'questions'
        )


class ShortTestSerializer(serializers.ModelSerializer):

    test_count = serializers.SerializerMethodField()
    start_time = serializers.DateTimeField(format='%Y/%m/%d')
    finish_time = serializers.DateTimeField(format='%Y/%m/%d')

    class Meta:
        model = m.Test
        fields = (
            'id', 'name', 'start_time', 'finish_time', 'test_count'
        )

    def get_test_count(self, instance):
        return instance.questions.all().count()


class TestSerializer(serializers.ModelSerializer):

    test_count = serializers.SerializerMethodField()
    appliant_count = serializers.SerializerMethodField()

    class Meta:
        model = m.Test
        fields = '__all__'

    def get_test_count(self, instance):
        return instance.questions.all().count()

    def get_appliant_count(self, instance):
        return instance.appliants.all().count()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['questions'] = ShortQuestionSerializer(instance.questions.all(), many=True).data
        ret['appliants'] = ShortWheelUserWithDepartmentSerializer(instance.appliants.all(), many=True).data
        return ret


# class TestSerializer(serializers.ModelSerializer):

#     questions = QuestionSerializer(many=True)
#     appliants = ShortTestResult(many=True)

#     class Meta:
#         model = m.Test
#         fields = '__all__'
