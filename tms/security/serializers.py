from django.shortcuts import get_object_or_404
from rest_framework import serializers

from ..core import constants as c

# models
from . import models as m
from ..hr.models import StaffProfile

# serializers
from ..core.serializers import TMSChoiceField
from ..account.serializers import UserNameSerializer, MainUserSerializer, UserDepartmentSerializer
from ..hr.serializers import ShortDepartmentSerializer, ShortSecurityOfficerProfileSerializer


class ShortCompanyPolicySerializer(serializers.ModelSerializer):

    published_on = serializers.DateTimeField(format='%Y-%m-%d', required=False)
    author = MainUserSerializer(read_only=True)
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = m.CompanyPolicy
        exclude = (
            'is_published', 'content', 'departments'
        )

    def get_is_read(self, instance):
        policy_read = m.CompanyPolicyRead.objects.filter(
            policy=instance,
            user=self.context.get('user', None)
        ).first()
        return policy_read is not None and policy_read.is_read


class CompanyPolicyStatusSerializer(serializers.ModelSerializer):

    author = UserNameSerializer()
    total_user_count = serializers.SerializerMethodField()
    published_on = serializers.DateTimeField(format='%Y-%m-%d', required=False)
    departments = ShortDepartmentSerializer(many=True)

    class Meta:
        model = m.CompanyPolicy
        fields = (
            'id',
            'title',
            'author',
            'published_on',
            'is_published',
            'departments',
            'read_user_count',
            'total_user_count',
        )

    def get_total_user_count(self, instance):
        return StaffProfile.objects.filter(
            department__in=instance.departments.all()
        ).count()


class CompanyPolicySerializer(serializers.ModelSerializer):

    author = UserNameSerializer(read_only=True)
    departments = ShortDepartmentSerializer(many=True, read_only=True)
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

        instance = m.CompanyPolicy.objects.create(author=author, **validated_data)

        departments = self.context.get('departments', [])
        for department in departments:
            department = get_object_or_404(m.Department, id=department)
            instance.departments.add(department)

        return instance

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

        instance.departments.clear()

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        departments = self.context.get('departments', [])
        for department in departments:
            department = get_object_or_404(m.Department, id=department)
            instance.departments.add(department)

        instance.save()
        return instance


class CompanyPolicyReadSerializer(serializers.ModelSerializer):

    user = UserNameSerializer(read_only=True)
    recent_read_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)

    class Meta:
        model = m.CompanyPolicyRead
        exclude = (
            'policy',
        )


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

    start_time = serializers.DateTimeField(format='%Y/%m/%d')
    finish_time = serializers.DateTimeField(format='%Y/%m/%d')
    is_finished = serializers.SerializerMethodField()

    class Meta:
        model = m.Test
        fields = (
            'id',
            'name',
            'start_time',
            'finish_time',
            'question_count',
            'is_finished',
        )

    def get_is_finished(self, instance):
        return m.TestResult.objects.filter(
            test=instance,
            appliant=self.context.get('user')
        ).exists()


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
        ret['appliants'] = UserDepartmentSerializer(instance.appliants.all(), many=True).data
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
    appliant = MainUserSerializer()
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

    author = MainUserSerializer(read_only=True)
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
        ret['audiences'] = UserDepartmentSerializer(instance.audiences.all(), many=True).data
        return ret


class SecurityCheckPlanSerializer(serializers.ModelSerializer):

    from_date = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    to_date = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    created = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )

    class Meta:
        model = m.SecurityCheckPlan
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['department'] = ShortDepartmentSerializer(instance.department).data
        ret['security_officers'] = ShortSecurityOfficerProfileSerializer(
            instance.security_officers, many=True
        ).data

        return ret
