from django.db import models

from ..core.models import ApprovedModel
from ..account.models import StaffProfile


class RestRequest(ApprovedModel):

    staff = models.ForeignKey(
        StaffProfile,
        on_delete=models.CASCADE
    )

    category = models.CharField(
        max_length=1
    )

    from_date = models.DateField()

    to_date = models.DateField()
