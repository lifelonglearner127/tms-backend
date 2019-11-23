from django.db import models
from django.contrib.postgres.fields import ArrayField

from ..core import constants as c

from . import managers
# models
from ..core.models import TimeStampedModel, CreatedTimeModel
from ..account.models import User
from ..hr.models import Department, SecurityOfficerProfile


class CompanyPolicy(TimeStampedModel):

    title = models.CharField(
        max_length=100
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    published_on = models.DateTimeField(
        null=True,
        blank=True
    )

    is_published = models.BooleanField(
        default=False
    )

    departments = models.ManyToManyField(
        Department
    )

    content = models.TextField()

    @property
    def read_user_count(self):
        return self.reads.count()

    objects = models.Manager()
    published_content = managers.PublishedContentManager()
    unpublished_content = managers.UnPublishedContentManager()


class CompanyPolicyRead(models.Model):

    policy = models.ForeignKey(
        CompanyPolicy,
        on_delete=models.CASCADE,
        related_name='reads'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    is_read = models.BooleanField(
        default=True
    )

    recent_read_time = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        unique_together = [
            'policy',
            'user',
        ]


class Question(TimeStampedModel):

    title = models.CharField(
        max_length=100
    )

    question_type = models.PositiveIntegerField(
        choices=c.QUESTION_TYPE,
        default=c.QUESTION_TYPE_BOOLEN
    )

    question = models.TextField()

    point = models.PositiveIntegerField()

    choices = ArrayField(
        models.TextField()
    )

    answers = ArrayField(
        models.PositiveIntegerField()
    )

    # this field is only used in case of the question is boolean question
    is_correct = models.BooleanField(
        default=False
    )


class Test(TimeStampedModel):

    name = models.CharField(
        max_length=100
    )

    start_time = models.DateTimeField()

    finish_time = models.DateTimeField()

    description = models.TextField(
        null=True,
        blank=True
    )

    questions = models.ManyToManyField(
        Question
    )

    appliants = models.ManyToManyField(
        User
    )

    @property
    def question_count(self):
        return self.questions.all().count()


class TestResult(models.Model):

    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE
    )

    appliant = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    full_point = models.PositiveIntegerField(
        default=0
    )

    point = models.PositiveIntegerField(
        default=0
    )

    started_on = models.DateTimeField(
        null=True, blank=True
    )

    finished_on = models.DateTimeField(
        null=True, blank=True
    )

    questions = models.ManyToManyField(
        Question,
        through='TestQuestionResult'
    )


class TestQuestionResult(models.Model):

    test_result = models.ForeignKey(
        TestResult,
        on_delete=models.CASCADE
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )

    is_correct = models.BooleanField(
        null=True, blank=True
    )

    answers = ArrayField(
        models.PositiveIntegerField(),
        null=True,
        blank=True
    )


class SecurityLibrary(TimeStampedModel):

    title = models.CharField(
        max_length=200
    )

    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    is_all = models.BooleanField(
        default=False
    )

    departments = models.ManyToManyField(
        Department
    )

    is_published = models.BooleanField(
        default=False
    )

    description = models.TextField(
        null=True,
        blank=True
    )


class SecurityLibraryAttachment(models.Model):

    library = models.ForeignKey(
        SecurityLibrary,
        on_delete=models.CASCADE,
        related_name='attachments'
    )

    attachment = models.FileField()


class SecurityLearningProgram(TimeStampedModel):

    name = models.CharField(
        max_length=200
    )

    start_time = models.DateTimeField()

    finish_time = models.DateTimeField()

    place = models.CharField(
        max_length=200
    )

    description = models.TextField(
        null=True,
        blank=True,
    )

    audiences = models.ManyToManyField(
        User
    )


class SecurityCheckPlan(CreatedTimeModel):

    from_date = models.DateTimeField()

    to_date = models.DateTimeField()

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    check_address = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    leader = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    check_content = models.TextField()

    check_result = models.TextField(
        null=True,
        blank=True
    )

    is_published = models.BooleanField(
        default=False
    )

    security_officers = models.ManyToManyField(
        SecurityOfficerProfile
    )
