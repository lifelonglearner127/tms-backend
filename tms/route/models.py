from django.db import models
from django.contrib.postgres.fields import ArrayField

# models
from ..core.models import TimeStampedModel
from ..info.models import Station
from ..vehicle.models import Vehicle


class Route(TimeStampedModel):

    name = models.CharField(
        max_length=100,
    )

    start_point = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name='routes_as_start_point'
    )

    end_point = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name='routes_as_end_point'
    )

    is_g7_route = models.BooleanField(
        default=False
    )

    # this field is used for storing middle points
    map_path = ArrayField(
        models.PositiveIntegerField(),
        null=True
    )

    # this field is used for storing location points from g7
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        null=True
    )

    start_time = models.DateTimeField(
        null=True,
        blank=True
    )

    finish_time = models.DateTimeField(
        null=True,
        blank=True
    )

    g7_path = ArrayField(
        ArrayField(
            models.DecimalField(
                max_digits=10,
                decimal_places=2
            ),
            size=2
        ),
        null=True
    )

    distance = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=3
    )

    def __str__(self):
        return self.name
