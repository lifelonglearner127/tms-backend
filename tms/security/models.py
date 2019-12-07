from django.db import models
from django.contrib.postgres.fields import ArrayField

from ..core import constants as c

from . import managers
# models
from ..core.models import TimeStampedModel, CreatedTimeModel
from ..account.models import User
from ..hr.models import Department, SecurityOfficerProfile
from ..vehicle.models import Vehicle


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


class SecurityIssue(TimeStampedModel):

    SECUIRTY_ISSUE_TYPE_0 = 0
    SECUIRTY_ISSUE_TYPE_1 = 1
    SECUIRTY_ISSUE_TYPE_2 = 2
    SECUIRTY_ISSUE_TYPE_3 = 3
    SECUIRTY_ISSUE_TYPE_4 = 4
    SECUIRTY_ISSUE_TYPE_5 = 5
    SECUIRTY_ISSUE_TYPE_6 = 6
    SECUIRTY_ISSUE_TYPE_7 = 7
    SECUIRTY_ISSUE_TYPE_8 = 8
    SECUIRTY_ISSUE_TYPE_9 = 9
    SECUIRTY_ISSUE_TYPE_10 = 10
    SECUIRTY_ISSUE_TYPE_11 = 11
    SECUIRTY_ISSUE_TYPE_12 = 12
    SECUIRTY_ISSUE_TYPE_13 = 13
    SECUIRTY_ISSUE_TYPE_14 = 14
    SECUIRTY_ISSUE_TYPE_15 = 15
    SECUIRTY_ISSUE_TYPE_16 = 16
    SECUIRTY_ISSUE_TYPE_17 = 17
    SECUIRTY_ISSUE_TYPE_18 = 18
    SECUIRTY_ISSUE_TYPE_19 = 19
    SECUIRTY_ISSUE_TYPE_20 = 20

    SECUIRTY_ISSUE_TYPE = (
        (SECUIRTY_ISSUE_TYPE_0, '车辆保养'),
        (SECUIRTY_ISSUE_TYPE_1, '换季保养'),
        (SECUIRTY_ISSUE_TYPE_2, '主车保轮'),
        (SECUIRTY_ISSUE_TYPE_3, '挂车保轮'),
        (SECUIRTY_ISSUE_TYPE_4, '车辆电器路维修'),
        (SECUIRTY_ISSUE_TYPE_5, '轮胎维修'),
        (SECUIRTY_ISSUE_TYPE_6, '轮胎更换'),
        (SECUIRTY_ISSUE_TYPE_7, '附属设备维修'),
        (SECUIRTY_ISSUE_TYPE_8, '中集设备维修'),
        (SECUIRTY_ISSUE_TYPE_9, '车辆救援费用'),
        (SECUIRTY_ISSUE_TYPE_10, '车辆物品配备车辆保养'),
        (SECUIRTY_ISSUE_TYPE_11, '换季保养'),
        (SECUIRTY_ISSUE_TYPE_12, '主车保轮'),
        (SECUIRTY_ISSUE_TYPE_13, '挂车保轮'),
        (SECUIRTY_ISSUE_TYPE_14, '车辆电器路维修'),
        (SECUIRTY_ISSUE_TYPE_15, '轮胎维修'),
        (SECUIRTY_ISSUE_TYPE_16, '轮胎更换'),
        (SECUIRTY_ISSUE_TYPE_17, '附属设备维修'),
        (SECUIRTY_ISSUE_TYPE_18, '中集设备维修'),
        (SECUIRTY_ISSUE_TYPE_19, '车辆救援费用'),
        (SECUIRTY_ISSUE_TYPE_20, '车辆物品配备'),
    )

    SECUIRTY_ISSUE_STATUS_WAITING_REPAIR = 1
    SECUIRTY_ISSUE_STATUS_WAITING_ACCEPTANCE = 2
    SECUIRTY_ISSUE_STATUS_COMPLETE = 3

    SECUIRTY_ISSUE_STATUS = (
        (SECUIRTY_ISSUE_STATUS_WAITING_REPAIR, '等待修理'),
        (SECUIRTY_ISSUE_STATUS_WAITING_ACCEPTANCE, '等待验收'),
        (SECUIRTY_ISSUE_STATUS_COMPLETE, '完毕'),
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    issue_type = models.PositiveIntegerField(
        default=SECUIRTY_ISSUE_TYPE_0,
        choices=SECUIRTY_ISSUE_TYPE
    )

    checker = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    check_content = models.TextField(
        null=True,
        blank=True
    )

    checked_on = models.DateField(
        null=True,
        blank=True
    )

    issue_status = models.PositiveIntegerField(
        default=SECUIRTY_ISSUE_STATUS_WAITING_REPAIR,
        choices=SECUIRTY_ISSUE_STATUS
    )

    rectifiers = models.ManyToManyField(
        User,
        through='SecurityIssueRectifier',
        through_fields=('security_issue', 'rectifier'),
        related_name='security_issues_as_rectifier'
    )

    acceptors = models.ManyToManyField(
        User,
        through='SecurityIssueAcceptor',
        through_fields=('security_issue', 'acceptor'),
        related_name='security_issues_as_acceptors'
    )

    ccs = models.ManyToManyField(
        User,
        through='SecurityIssueCC',
        through_fields=('security_issue', 'cc'),
        related_name='security_issues_as_ccs'
    )


class SecurityIssueRectifier(TimeStampedModel):

    security_issue = models.ForeignKey(
        SecurityIssue,
        on_delete=models.CASCADE
    )

    rectifier = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    rectified_on = models.DateTimeField(
        null=True,
        blank=True
    )

    description = models.TextField(
        null=True,
        blank=True
    )


class SecurityIssueAcceptor(TimeStampedModel):

    security_issue = models.ForeignKey(
        SecurityIssue,
        on_delete=models.CASCADE
    )

    acceptor = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    accepted_on = models.DateTimeField(
        null=True,
        blank=True
    )

    description = models.TextField(
        null=True,
        blank=True
    )


class SecurityIssueCC(TimeStampedModel):

    security_issue = models.ForeignKey(
        SecurityIssue,
        on_delete=models.CASCADE
    )

    cc = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    cc_on = models.DateTimeField(
        null=True,
        blank=True
    )

    description = models.TextField(
        null=True,
        blank=True
    )
