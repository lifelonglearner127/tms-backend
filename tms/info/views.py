from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from ..core import constants as c

# models
from . import models as m

# permissions
from . import permissions as p

# serializers
from . import serializers as s
from ..core.serializers import ChoiceSerializer

# views
from ..core.views import TMSViewSet, StaffAPIView


class BasicSettingAPIView(StaffAPIView):

    def get(self, request):
        instance = m.BasicSetting.objects.first()
        if instance is None:
            return Response(
                None,
                status=status.HTTP_200_OK
            )

        return Response(
            s.BasicSettingSerializer(instance).data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        instance = m.BasicSetting.objects.first()
        if instance is None:
            serializer = s.BasicSettingSerializer(
                data=request.data
            )
        else:
            serializer = s.BasicSettingSerializer(
                instance,
                data=request.data,
                partial=True
            )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class TaxRateAPIView(APIView):

    def get(self, request):
        instance = m.BasicSetting.objects.first()

        if instance is None:
            tax_rate = 0
        else:
            tax_rate = instance.tax_rate

        ret = {
            'tax_rate': tax_rate
        }

        return Response(
            ret,
            status=status.HTTP_200_OK
        )


# class ProductCategoryViewSet(TMSViewSet):

#     queryset = m.ProductCategory.objects.all()
#     serializer_class = s.ProductCategorySerializer
#     short_serializer_class = s.ShortProductCategorySerializer


class ProductViewSet(TMSViewSet):
    """
    Viewset for products
    """
    queryset = m.Product.objects.all()
    serializer_class = s.ProductSerializer
    short_serializer_class = s.ShortProductSerializer
    permission_classes = [p.ProductViewSetPermission]

    # def create(self, request):
    #     context = {
    #         'category': request.data.pop('category')
    #     }

    #     serializer = s.ProductSerializer(
    #         data=request.data, context=context
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(
    #         serializer.data,
    #         status=status.HTTP_200_OK
    #     )

    # def update(self, request, pk=None):
    #     instance = self.get_object()
    #     context = {
    #         'category': request.data.pop('category')
    #     }

    #     serializer = s.ProductSerializer(
    #         instance, data=request.data, context=context
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(
    #         serializer.data,
    #         status=status.HTTP_200_OK
    #     )

    # @action(detail=False, url_path="categories")
    # def get_product_cateogires(self, request):
    #     serializer = ChoiceSerializer(
    #         [
    #             {'value': x, 'text': y} for (x, y) in c.PRODUCT_CATEGORY
    #         ],
    #         many=True
    #     )
    #     return Response(
    #         serializer.data,
    #         status=status.HTTP_200_OK
    #     )


class StationViewSet(TMSViewSet):
    """
    Viewset for Loading Station
    """
    queryset = m.Station.objects.all()
    serializer_class = s.StationSerializer

    def get_queryset(self):
        queryset = self.queryset
        station_type = self.request.query_params.get('station_type', None)
        if station_type is not None:
            queryset = queryset.filter(station_type=station_type)

        return queryset

    def create(self, request):
        products = request.data.pop('products', [])
        if request.user.user_type == c.USER_TYPE_CUSTOMER:
            customers = [{
                'id': request.user.customer_profile.id
            }]
        else:
            customers = request.data.pop('customers', [])

        serializer = s.StationSerializer(
            data=request.data,
            context={
                'products': products,
                'customers': customers
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
        products = request.data.pop('products', [])
        if request.user.user_type == c.USER_TYPE_CUSTOMER:
            customers = [{
                'id': request.user.customer_profile.id
            }]
        else:
            customers = request.data.pop('customers', [])

        serializer = s.StationSerializer(
            instance,
            data=request.data,
            context={
                'products': products,
                'customers': customers
            },
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='short')
    def get_short_stations(self, request):

        station_type_filter = Q()

        station_types = self.request.query_params.get('station_type', '')
        station_types = station_types.split(',')

        for station_type in station_types:
            if station_type in [
                c.STATION_TYPE_LOADING_STATION,
                c.STATION_TYPE_UNLOADING_STATION,
                c.STATION_TYPE_QUALITY_STATION,
                c.STATION_TYPE_OIL_STATION,
                c.STATION_TYPE_GET_OFF_STATION,
                c.STATION_TYPE_BLACK_DOT,
                c.STATION_TYPE_PARKING_STATION,
                c.STATION_TYPE_REPAIR_STATION,
            ]:
                station_type_filter |= Q(station_type=station_type)

        queryset = m.Station.objects.filter(station_type_filter)

        return Response(
            s.ShortStationSerializer(queryset, many=True).data,
            status=status.HTTP_200_OK
        )

    # @action(detail=False, url_path='')
    # def get_short_work_stations_with_lnglat(self, request):
    #     """
    #     api is used in routing page
    #     """
    #     queryset = m.Station.workstations.all()
    #     station_type = self.request.query_params.get('station_type', '')
    #     if station_type in [
    #         c.STATION_TYPE_LOADING_STATION,
    #         c.STATION_TYPE_QUALITY_STATION,
    #         c.STATION_TYPE_UNLOADING_STATION,
    #     ]:
    #         queryset = queryset.filter(station_type=station_type)

    #     return Response(
    #         s.StationForRouteSerializer(queryset).data,
    #         status=status.HTTP_200_OK
    #     )

    # @action(detail=False, url_path='short')
    # def short(self, request):
    #     station_type = self.request.query_params.get('type', None)
    #     if station_type in [
    #         c.STATION_TYPE_LOADING_STATION, c.STATION_TYPE_UNLOADING_STATION,
    #         c.STATION_TYPE_OIL_STATION, c.STATION_TYPE_QUALITY_STATION
    #     ]:
    #         queryset = m.Station.objects.filter(station_type=station_type)
    #     else:
    #         queryset = self.get_queryset()

    #     serializer = s.ShortStationSerializer(queryset, many=True)

    #     return Response(
    #         serializer.data,
    #         status=status.HTTP_200_OK
    #     )

    #     return queryset

    # @action(detail=False, url_path='short/names')
    # def get_station_names(self, request):
    #     station_type = self.request.query_params.get('type', None)
    #     if station_type in [
    #         c.STATION_TYPE_LOADING_STATION,
    #         c.STATION_TYPE_UNLOADING_STATION,
    #         c.STATION_TYPE_QUALITY_STATION,
    #         c.STATION_TYPE_OIL_STATION,
    #         c.STATION_TYPE_BLACK_DOT,
    #         c.STATION_TYPE_PARKING_STATION,
    #         c.STATION_TYPE_REPAIR_STATION,
    #     ]:
    #         queryset = m.Station.objects.filter(station_type=station_type)
    #     else:
    #         queryset = self.get_queryset()

    #     serializer = s.StationNameSerializer(queryset, many=True)

    #     return Response(
    #         serializer.data,
    #         status=status.HTTP_200_OK
    #     )

    #     return queryset

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

    @action(detail=False, url_path='black-dots')
    def black_dots(self, request):
        page = self.paginate_queryset(
            m.Station.blackdots.all(),
        )

        serializer = s.BlackDotSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='parking-stations')
    def parking_stations(self, request):
        page = self.paginate_queryset(
            m.Station.parkingstations.all(),
        )

        serializer = s.ParkingStationSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='getoff-stations')
    def getoff_stations(self, request):
        page = self.paginate_queryset(
            m.Station.getoffstations.all(),
        )

        serializer = s.GetoffStationSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='me')
    def get_customer_stations(self, request):
        """
        This api endpoint is for customer app
        """
        station_type = self.request.query_params.get(
            'type', None
        )

        queryset = m.Station.objects.filter(customers=request.user.customer_profile)

        if station_type:
            queryset = queryset.filter(station_type=station_type)

        page = self.paginate_queryset(queryset)
        serializer = s.WorkStationSerializer(page, many=True)

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



class TransportationDistanceViewSet(TMSViewSet):

    queryset = m.TransportationDistance.objects.all()
    serializer_class = s.TransportationDistanceSerializer

    def create(self, request):
        context = {
            'start_point': request.data.pop('start_point'),
            'end_point': request.data.pop('end_point')
        }
        serializer = s.TransportationDistanceSerializer(
            data=request.data,
            context=context
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        context = {
            'start_point': request.data.pop('start_point'),
            'end_point': request.data.pop('end_point')
        }
        serializer = s.TransportationDistanceSerializer(
            instance,
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
