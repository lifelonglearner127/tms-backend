from rest_framework import serializers

from ..core import constants as c

# models
from . import models as m

# serializers
from ..core.serializers import TMSChoiceField
from ..account.serializers import ShortUserSerializer


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


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Answer
        exclude = ('question', )


class QuestionSerializer(serializers.ModelSerializer):

    question_type = TMSChoiceField(choices=c.QUESTION_TYPE)
    answers = serializers.SerializerMethodField()
    created = serializers.DateTimeField(
        format='%Y-%m-%d', required=False
    )

    class Meta:
        model = m.Question
        fields = '__all__'

    def create(self, validated_data):
        answers = self.context.get('answers', [])
        question = m.Question.objects.create(**validated_data)

        for answer in answers:
            m.Answer.objects.create(
                question=question, **answer
            )

        return question

    def update(self, instance, validated_data):
        answers = self.context.get('answers', [])

        if instance.question_type in [c.QUESTION_TYPE_SINGLE_CHOICE, c.QUESTION_TYPE_MULTIPLE_CHOICE]:
            instance.answers.all().delete()

        for key, value in validated_data.items():
            setattr(instance, key, value)

        for answer in answers:
            m.Answer.objects.create(
                question=instance, **answer
            )

        instance.save()
        return instance

    def get_answers(self, instance):
        ret = []
        for answer in instance.answers:
            ret.append(AnswerSerializer(answer).data)

        return ret


class ShortTestResult(serializers.ModelSerializer):

    class Meta:
        model = m.TestResult
        exclude = (
            'questions'
        )


class TestCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Test
        fields = '__all__'


class TestSerializer(serializers.ModelSerializer):

    questions = QuestionSerializer(many=True)
    appliants = ShortTestResult(many=True)

    class Meta:
        model = m.Test
        fields = (
            'id', 'questions', 'appliants'
        )
