from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

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


class StationViewSet(StaffViewSet):
    """
    Viewset for Loading Station
    """
    queryset = m.Station.objects.all()
    short_serializer_class = s.ShortStationSerializer

    def get_serializer_class(self):
        if self.action in ['list']:
            return s.StationInfoSerializer
        else:
            return s.StationSerializer

    @action(detail=False)
    def short(self, request):
        station_type = self.request.query_params.get('type', None)
        if station_type in [
            c.STATION_TYPE_LOADING_STATION, c.STATION_TYPE_UNLOADING_STATION,
            c.STATION_TYPE_OIL_STATION, c.STATION_TYPE_QUALITY_STATION
        ]:
            queryset = m.Station.objects.filter(station_type=station_type)
        else:
            queryset = self.get_queryset()

        serializer = self.get_short_serializer_class()(
            queryset,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

        return queryset
        # serializer = self.get_short_serializer_class()(
        #     self.get_queryset(),
        #     many=True
        # )
        # return Response(
        #     serializer.data,
        #     status=status.HTTP_200_OK
        # )
    
    @action(detail=False, url_path='loading-stations')
    def loading_stations(self, request):
        page = self.paginate_queryset(
            m.Station.loading.all(),
        )

        serializer = self.get_serializer_class()(
            page,
            many=True
        )

        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='unloading-stations')
    def unloading_stations(self, request):
        page = self.paginate_queryset(
            m.Station.unloading.all(),
        )

        serializer = self.get_serializer_class()(
            page,
            many=True
        )

        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='quality-stations')
    def quality_stations(self, request):
        page = self.paginate_queryset(
            m.Station.quality.all(),
        )

        serializer = self.get_serializer_class()(
            page,
            many=True
        )

        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='oil-stations')
    def oil_stations(self, request):
        page = self.paginate_queryset(
            m.Station.oil.all(),
        )

        serializer = self.get_serializer_class()(
            page,
            many=True
        )

        return self.get_paginated_response(serializer.data)


class ProductCategoriesView(ChoicesView):
    """
    APIView for returning product categories
    """
    static_choices = c.PRODUCT_TYPE
