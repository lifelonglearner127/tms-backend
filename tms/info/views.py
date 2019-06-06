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
    serializer_class = s.ProductSerializer
    short_serializer_class = s.ShortProductSerializer


class StationViewSet(StaffViewSet):
    """
    Viewset for Loading Station
    """
    queryset = m.Station.objects.all()

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

        serializer = s.ShortStationSerializer(queryset, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

        return queryset

    @action(detail=False, url_path='loading-stations')
    def loading_stations(self, request):
        page = self.paginate_queryset(
            m.Station.loading.all(),
        )

        serializer = s.WorkStationSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='unloading-stations')
    def unloading_stations(self, request):
        page = self.paginate_queryset(
            m.Station.unloading.all(),
        )

        serializer = s.WorkStationSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='quality-stations')
    def quality_stations(self, request):
        page = self.paginate_queryset(
            m.Station.quality.all(),
        )

        serializer = s.WorkStationSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='oil-stations')
    def oil_stations(self, request):
        page = self.paginate_queryset(
            m.Station.oil.all(),
        )

        serializer = s.OilStationSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)


class ProductCategoriesView(ChoicesView):
    """
    APIView for returning product categories
    """
    static_choices = c.PRODUCT_TYPE
