from django.db import models

from ..core import constants as c

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
