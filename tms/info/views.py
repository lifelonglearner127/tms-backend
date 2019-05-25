from ..core.views import StaffViewSet, ChoicesView
from ..core import constants as c
from . import models as m
from . import serializers as s


class ProductViewSet(StaffViewSet):
    """
    Viewset for products
    """
    queryset = m.Product.objects.all()
    short_serializer_class = s.ShortProductSerializer

    def get_serializer_class(self):
        if self.action in ['list']:
            return s.ProductInfoSerializer
        else:
            return s.ProductSerializer


class LoadingStationViewSet(StaffViewSet):
    """
    Viewset for Loading Station
    """
    queryset = m.LoadingStation.objects.all()
    short_serializer_class = s.ShortLoadingStationSerializer

    def get_serializer_class(self):
        if self.action in ['list']:
            return s.LoadingStationInfoSerializer
        else:
            return s.LoadingStationSerializer


class UnLoadingStationViewSet(StaffViewSet):
    """
    Viewset for UnLoading Station
    """
    queryset = m.UnLoadingStation.objects.all()
    short_serializer_class = s.ShortUnLoadingStationSerializer

    def get_serializer_class(self):
        if self.action in ['list']:
            return s.UnLoadingStationInfoSerializer
        else:
            return s.UnLoadingStationSerializer


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
    static_choices = c.PRODUCT_TYPE
