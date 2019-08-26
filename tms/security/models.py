from django.db import models

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

    question_type = models.CharField(
        max_length=1,
        choices=c.QUESTION_TYPE,
        default=c.QUESTION_TYPE_BOOLEN
    )

    question = models.TextField()

    point = models.PositiveIntegerField()

    # this field is only used in case of the question is boolean question
    is_correct = models.BooleanField(
        default=False
    )


class Answer(models.Model):

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers'
    )

    anwser = models.TextField()

    is_correct = models.BooleanField(
        default=False
    )


class Test(TimeStampedModel):

    questions = models.ManyToManyField(
        Question
    )

    appliants = models.ManyToManyField(
        User,
        through='TestResult',
        through_fields=('test', 'appliant')
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
        through='TestResultQuestion'
    )


class TestResultQuestion(models.Model):

    test_result = models.ForeignKey(
        TestResult,
        on_delete=models.CASCADE
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )

    is_correct = models.BooleanField(
        default=False
    )

    answer = models.ManyToManyField(
        Answer,
        through='TestResultQuestionAnswer',
        through_fields=('test_result_question', 'answer')
    )


class TestResultQuestionAnswer(models.Model):

    test_result_question = models.ForeignKey(
        TestResultQuestion,
        on_delete=models.CASCADE
    )

    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE
    )

    is_correct = models.BooleanField(
        default=False
    )
