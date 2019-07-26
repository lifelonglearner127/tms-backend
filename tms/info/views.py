from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..core import constants as c

# models
from . import models as m

# serializers
from . import serializers as s
from ..core.serializers import ChoiceSerializer

# views
from ..core.views import StaffViewSet, TMSViewSet


class ProductViewSet(StaffViewSet):
    """
    Viewset for products
    """
    queryset = m.Product.objects.all()
    serializer_class = s.ProductSerializer
    short_serializer_class = s.ShortProductSerializer

    @action(detail=False, url_path="categories")
    def get_product_cateogires(self, request):
        serializer = ChoiceSerializer(
            [
                {'value': x, 'text': y} for (x, y) in c.PRODUCT_CATEGORY
            ],
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class StationViewSet(TMSViewSet):
    """
    Viewset for Loading Station
    """
    queryset = m.Station.objects.all()
    serializer_class = s.StationSerializer

    def create(self, request):
        products = request.data.pop('products', None)
        if request.user.role == c.USER_ROLE_CUSTOMER:
            customer = {
                'id': request.user.customer_profile.id
            }
        else:
            customer = request.data.pop('customer', None)

        serializer = s.StationSerializer(
            data=request.data,
            context={
                'products': products,
                'customer': customer
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        products = request.data.pop('products', None)
        if request.user.role == c.USER_ROLE_CUSTOMER:
            customer = {
                'id': request.user.customer_profile.id
            }
        else:
            customer = request.data.pop('customer', None)

        customer = request.data.pop('customer', None)
        serializer = s.StationSerializer(
            instance,
            data=request.data,
            context={
                'products': products,
                'customer': customer
            },
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
            m.Station.loadingstations.all(),
        )

        serializer = s.WorkStationSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='unloading-stations')
    def unloading_stations(self, request):
        page = self.paginate_queryset(
            m.Station.unloadingstations.all(),
        )

        serializer = s.WorkStationSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='quality-stations')
    def quality_stations(self, request):
        page = self.paginate_queryset(
            m.Station.qualitystations.all(),
        )

        serializer = s.WorkStationSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='oil-stations')
    def oil_stations(self, request):
        page = self.paginate_queryset(
            m.Station.oilstations.all(),
        )

        serializer = s.OilStationSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='me')
    def get_customer_stations(self, request):
        """
        This api endpoint is for customer app
        """
        station_type = self.request.query_params.get(
            'type', None
        )

        queryset = m.Station.objects.filter(
            customer=request.user.customer_profile
        )
        if station_type:
            queryset = queryset.filter(station_type=station_type)

        page = self.paginate_queryset(queryset)
        serializer = s.WorkStationSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='black-dots')
    def black_dots(self, request):
        page = self.paginate_queryset(
            m.Station.blackdots.all(),
        )

        serializer = s.BlackDotSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='points')
    def get_station_points(self, request):
        queryset = m.Station.workstations.all()
        station_types = self.request.query_params.get('type', None)

        if station_types is not None:
            station_type_filter = Q()
            station_types = station_types.split(',')
            for station_type in station_types:
                if station_type in [
                    c.STATION_TYPE_LOADING_STATION,
                    c.STATION_TYPE_UNLOADING_STATION,
                    c.STATION_TYPE_QUALITY_STATION,
                    c.STATION_TYPE_OIL_STATION
                ]:
                    station_type_filter |= Q(station_type=station_type)
            queryset = queryset.filter(station_type_filter)

        serializer = s.StationPointSerializer(
            queryset, many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class RouteViewSet(TMSViewSet):

    queryset = m.Route.objects.all()
    serializer_class = s.RouteSerializer
    short_serializer_class = s.ShortRouteSerializer
    data_view_serializer_class = s.RouteDataViewSerializer

    @action(detail=True, url_path='points', methods=['get'])
    def get_route_point(self, request, pk=None):
        instance = self.get_object()
        return Response(
            s.RoutePointSerializer(instance).data,
            status=status.HTTP_200_OK
        )
