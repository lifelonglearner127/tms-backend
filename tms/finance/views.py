from . import models as m
from . import serializers as s
from ..core.views import TMSViewSet


class OrderPaymentViewSet(TMSViewSet):

    queryset = m.OrderPayment.objects.all()
    serializer_class = s.OrderPaymentSerializer
    data_view_serializer_class = s.OrderPaymentDataViewSerializer


class ETCCardViewSet(TMSViewSet):

    queryset = m.ETCCard.objects.all()
    serializer_class = s.ETCCardSerializer
    short_serializer_class = s.ShortETCCardSerializer
    data_view_serializer_class = s.ETCCardDataViewSerializer


class FuelCardViewSet(TMSViewSet):

    queryset = m.FuelCard.objects.all()
    serializer_class = s.FuelCardSerializer
    short_serializer_class = s.ShortFuelCardSerializer
    data_view_serializer_class = s.FuelCardDataViewSerializer
