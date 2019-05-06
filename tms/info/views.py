from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from ..core.views import StaffAPIView, StaffViewSet
from ..core.constants import PRODUCT_TYPE
from . import models
from . import serializers


class ProductViewSet(StaffViewSet):

    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer


class ShortProductView(StaffAPIView):

    def get(self, request):
        serializer = serializers.ShortProductSerializer(
            models.Product.objects.all(),
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class ProductCategoriesView(StaffAPIView):

    def get(self, request):
        product_categories = []
        for (slug, name) in PRODUCT_TYPE:
            product_categories.append(
                {
                    'value': slug,
                    'text': name
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

    def create(self, request):
        context = {
            'product_id': request.data.pop('product')
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
            'product_id': request.data.pop('product')
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
        

class UnLoadingStationViewSet(StaffViewSet):

    queryset = models.UnLoadingStation.objects.all()
    serializer_class = serializers.UnLoadingStationSerializer

    def create(self, request):
        context = {
            'product_id': request.data.pop('product')
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
            'product_id': request.data.pop('product')
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


class QualityStationViewSet(StaffViewSet):

    queryset = models.QualityStation.objects.all()
    serializer_class = serializers.QualityStationSerializer


class OilStationViewSet(StaffViewSet):

    queryset = models.OilStation.objects.all()
    serializer_class = serializers.OilStationSerializer
