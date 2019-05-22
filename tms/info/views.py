from ..core.views import StaffViewSet, ChoicesView
from ..core.constants import PRODUCT_TYPE
from . import models as m
from . import serializers as s


class ProductViewSet(StaffViewSet):
    """
    Viewset for products
    """
    queryset = m.Product.objects.all()
    serializer_class = s.ProductSerializer
    short_serializer_class = s.ShortProductSerializer


class LoadingStationViewSet(StaffViewSet):
    """
    Viewset for Loading Station
    """
    queryset = m.LoadingStation.objects.all()
    serializer_class = s.LoadingStationSerializer
    short_serializer_class = s.ShortLoadingStationSerializer


class UnLoadingStationViewSet(StaffViewSet):
    """
    Viewset for UnLoading Station
    """
    queryset = m.UnLoadingStation.objects.all()
    serializer_class = s.UnLoadingStationSerializer
    short_serializer_class = s.ShortUnLoadingStationSerializer


class QualityStationViewSet(StaffViewSet):
    """
    Viewset for Quality Station
    """
    queryset = m.QualityStation.objects.all()
    serializer_class = s.QualityStationSerializer


class OilStationViewSet(StaffViewSet):
    """
    Viewset for Oil Station
    """
    queryset = m.OilStation.objects.all()
    serializer_class = s.OilStationSerializer


class ProductCategoriesView(ChoicesView):
    """
    APIView for returning product categories
    """
    static_choices = PRODUCT_TYPE
