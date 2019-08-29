from django.db import models
from django.contrib.postgres.fields import ArrayField

from ..core import constants as c

from . import managers
# models
from ..core.models import TimeStampedModel
from ..account.models import User


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

    policy_type = models.CharField(
        max_length=1,
        choices=c.COMPANY_POLICY_TYPE,
        default=c.COMPANY_POLICY_TYPE_SHELL
    )

    content = models.TextField()

    objects = models.Manager()
    published_content = managers.PublishedContentManager()
    unpublished_content = managers.UnPublishedContentManager()


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
