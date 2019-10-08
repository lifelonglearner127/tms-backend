from django.shortcuts import get_object_or_404
from rest_framework import serializers

from ..core import constants as c

# models
from . import models as m

# serializers
from ..core.serializers import TMSChoiceField
from ..account.serializers import ShortUserSerializer, ShortUserWithDepartmentSerializer
from ..hr.serializers import ShortDepartmentSerializer


class ShortCompanyPolicySerializer(serializers.ModelSerializer):

    policy_type = TMSChoiceField(c.COMPANY_POLICY_TYPE)
    published_on = serializers.DateTimeField(format='%Y-%m-%d', required=False)
    author = ShortUserSerializer(read_only=True)
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = m.CompanyPolicy
        exclude = (
            'is_published', 'content'
        )

    def get_is_read(self, instance):
        return m.CompanyPolicyRead.objects.filter(
            policy=instance,
            user=self.context.get('user', None)
        ).exists()


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
        except m.User.DoesNotExist:
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
        except m.User.DoesNotExist:
            raise serializers.ValidationError({
                'author': 'Such user does not exits'
            })

        instance.author = author
        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


class CompanyPolicyReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.CompanyPolicy
        fields = '__all__'


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
        ret['appliants'] = ShortUserWithDepartmentSerializer(instance.appliants.all(), many=True).data
        return ret


class ShortTestResult(serializers.ModelSerializer):

    class Meta:
        model = m.TestResult
        exclude = (
            'questions'
        )


class TestQuestionResultSerializer(serializers.ModelSerializer):

    question = QuestionSerializer()

    class Meta:
        model = m.TestQuestionResult
        exclude = (
            'test_result',
        )


class TestResultSerializer(serializers.ModelSerializer):

    test = ShortTestSerializer()
    appliant = ShortUserSerializer()
    questions = TestQuestionResultSerializer(
        source='testquestionresult_set', many=True
    )

    started_on = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)
    finished_on = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)

    class Meta:
        model = m.TestResult
        fields = '__all__'


class ShortSecurityLibraryAttachmentSerializer(serializers.ModelSerializer):

    name = serializers.CharField(source='attachment.name')
    size = serializers.CharField(source='attachment.size')

    class Meta:
        model = m.SecurityLibraryAttachment
        fields = (
            'id', 'attachment', 'name', 'size'
        )


class SecurityLibraryAttachmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.SecurityLibraryAttachment
        fields = '__all__'


class SecurityLibrarySerializer(serializers.ModelSerializer):

    author = ShortUserSerializer(read_only=True)
    departments = ShortDepartmentSerializer(read_only=True, many=True)
    attachments = serializers.SerializerMethodField()

    class Meta:
        model = m.SecurityLibrary
        fields = '__all__'

    def create(self, validated_data):
        author_data = self.context.get('author')
        departments_data = self.context.get('departments', [])
        try:
            author = m.User.objects.get(id=author_data.get('id', None))
        except m.User.DoesNotExist:
            raise serializers.ValidationError({
                'author': 'cannot find such user'
            })

        library = m.SecurityLibrary.objects.create(
            author=author,
            **validated_data
        )
        for department_data in departments_data:
            department = get_object_or_404(m.Department, id=department_data.get('id', None))
            library.departments.add(department)
        return library

    def update(self, instance, validated_data):
        author_data = self.context.get('author')
        departments_data = self.context.get('departments', [])
        try:
            author = m.User.objects.get(id=author_data.get('id', None))
        except m.User.DoesNotExist:
            raise serializers.ValidationError({
                'author': 'cannot find such user'
            })
        instance.author = author
        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.departments.clear()
        for department_data in departments_data:
            department = get_object_or_404(m.Department, id=department_data.get('id', None))
            instance.departments.add(department)

        instance.save()
        return instance

    def get_attachments(self, instance):
        ret = []
        for attachment in instance.attachments.all():
            ret.append(ShortSecurityLibraryAttachmentSerializer(
                attachment,
                context={'request': self.context.get('request')}
            ).data)

        return ret


class ShortSecurityLearningProgramSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.SecurityLearningProgram
        exclude = (
            'description',
            'audiences',
        )


class SecurityLearningProgramSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.SecurityLearningProgram
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['audiences'] = ShortUserWithDepartmentSerializer(instance.audiences.all(), many=True).data
        return ret
