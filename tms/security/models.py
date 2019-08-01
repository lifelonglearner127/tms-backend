from django.db import models

# models
from ..core.models import TimeStampedModel
from ..account.models import User


class CompanyContent(TimeStampedModel):

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

    content = models.TextField()

    class Meta:
        abstract = True


class CompanyPolicy(CompanyContent):
    pass


class SecurityKnowledge(CompanyContent):
    pass
