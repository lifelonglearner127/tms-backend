from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

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

    @action(detail=False)
    def short(self, request):
        serializer = s.ShortProductSerializer(
            m.Product.objects.all(),
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


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

    @action(detail=False)
    def short(self, request):
        serializer = s.ShortLoadingStationSerializer(
            m.LoadingStation.objects.all(),
            many=True
        )
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


class ProductCategoriesView(ChoicesView):
    """
    APIView for returning product categories
    """
    static_choices = PRODUCT_TYPE
