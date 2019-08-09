from django.db import models

from ..core import constants as c


class StationBillDocumentManager(models.Manager):
    """
    Manager for getting avaiable vehicles
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            category__in=[
                c.BILL_FROM_LOADING_STATION, c.BILL_FROM_QUALITY_STATION,
                c.BILL_FROM_UNLOADING_STATION
            ]
        )


class OtherBillDocumentManager(models.Manager):
    """
    Manager for getting avaiable vehicles
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            category__in=[
                c.BILL_FROM_OIL_STATION, c.BILL_FROM_TRAFFIC,
                c.BILL_FROM_OTHER
            ]
        )


class FuelMasterCards(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_child=False)


class FuelChildernCards(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_child=True)
