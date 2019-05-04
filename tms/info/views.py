from rest_framework import status
from rest_framework.response import Response

from ..core.views import StaffAPIView, StaffViewSet
from ..core.constants import PRODUCT_TYPE
from . import models
from . import serializers


class ProductViewSet(StaffViewSet):

    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer


class ProductCategoriesView(StaffAPIView):

    def get(self, request):
        product_categories = []
        for (slug, name) in PRODUCT_TYPE:
            product_categories.append(
                {
                    'slug': slug,
                    'name': name
                }
            )

        serializer = serializers.ProductCategoriesSerializer(
            product_categories,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class LoadingStationViewSet(StaffViewSet):

    queryset = models.LoadingStation.objects.all()
    serializer_class = serializers.LoadingStationSerializer


class UnLoadingStationViewSet(StaffViewSet):

    queryset = models.UnLoadingStation.objects.all()
    serializer_class = serializers.UnLoadingStationSerializer


class QualityStationViewSet(StaffViewSet):

    queryset = models.QualityStation.objects.all()
    serializer_class = serializers.QualityStationSerializer


class OilStationViewSet(StaffViewSet):

    queryset = models.OilStation.objects.all()
    serializer_class = serializers.OilStationSerializer
