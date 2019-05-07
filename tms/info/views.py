from rest_framework import status
from rest_framework.response import Response

from ..core.views import StaffViewSet, ShortAPIView, ChoicesView
from ..core.constants import PRODUCT_TYPE
from . import models as m
from . import serializers as s


class ProductViewSet(StaffViewSet):
    """
    Viewset for products
    """
    queryset = m.Product.objects.all()
    serializer_class = s.ProductSerializer


class LoadStationViewSet(StaffViewSet):
    """
    Used for base class for loading, unloading station viewset
    """
    def create(self, request):
        context = {
            'product': request.data.pop('product')
        }
        serializer = self.serializer_class(
            data=request.data,
            context=context
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        serializer_instance = self.get_object()
        context = {
            'product': request.data.pop('product')
        }
        serializer = self.serializer_class(
            serializer_instance,
            data=request.data,
            context=context,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class LoadingStationViewSet(LoadStationViewSet):
    """
    Viewset for Loading Station
    """
    queryset = m.LoadingStation.objects.all()
    serializer_class = s.LoadingStationSerializer


class UnLoadingStationViewSet(LoadStationViewSet):
    """
    Viewset for UnLoading Station
    """
    queryset = m.UnLoadingStation.objects.all()
    serializer_class = s.UnLoadingStationSerializer


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


class ShortProductAPIView(ShortAPIView):
    """
    View to list short data of product
    """
    model_class = m.Product
    serializer_class = s.ShortProductSerializer


class ShortLoadingStationAPIView(ShortAPIView):
    """
    View to list short data of loading stations
    """
    model_class = m.LoadingStation
    serializer_class = s.ShortLoadingStationSerializer


class ShortUnLoadingStationAPIView(ShortAPIView):
    """
    View to list short data of unloading stations
    """
    model_class = m.UnLoadingStation
    serializer_class = s.ShortUnLoadingStationSerializer


class ShortQualityStationAPIView(ShortAPIView):
    """
    View to list short data of quality stations
    """
    model_class = m.QualityStation
    serializer_class = s.QualityStationSerializer


class ShortOilStationAPIView(ShortAPIView):
    """
    View to list short data of oil stations
    """
    model_class = m.OilStation
    serializer_class = s.OilStationSerializer


class ProductCategoriesView(ChoicesView):

    static_choices = PRODUCT_TYPE
