from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models as m
from . import serializers as s
from ..core.views import TMSViewSet
from ..job.serializers import ShortJobSerializer


class OrderViewSet(TMSViewSet):
    """
    Order Viewset
    """
    queryset = m.Order.objects.all()
    serializer_class = s.OrderSerializer
    # data_view_serializer_class = s.OrderDataViewSerializer

    def create(self, request):
        context = {
            'loading_stations': request.data.pop('loading_stations'),
            'assignee': request.data.pop('assignee'),
            'customer': request.data.pop('customer')
        }

        serializer = s.OrderSerializer(
            data=request.data, context=context
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
            'loading_stations': request.data.pop('loading_stations'),
            'assignee': request.data.pop('assignee'),
            'customer': request.data.pop('customer')
        }

        serializer = s.OrderSerializer(
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

    def list(self, request):
        page = self.paginate_queryset(
            self.get_queryset().all()
        )

        serializer = s.OrderDataViewSerializer(
            page,
            many=True
        )

        return self.get_paginated_response(serializer.data)

    @action(detail=True, url_path='jobs')
    def get_jobs(self, request, pk=None):
        order = self.get_object()
        serializer = ShortJobSerializer(
            order.jobs.all(),
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class OrderLoadingStationViewSet(viewsets.ModelViewSet):
    """
    OrderProduct Viewset
    """
    serializer_class = s.OrderLoadingStationSerializer

    def get_queryset(self):
        return m.OrderLoadingStation.objects.filter(
            order__id=self.kwargs['order_pk']
        )


class OrderProductViewSet(viewsets.ModelViewSet):
    """
    OrderProduct Viewset
    """
    serializer_class = s.OrderProductSerializer

    def get_queryset(self):
        return m.OrderProduct.objects.filter(
            order_loading_station__id=self.kwargs['orderloadingstation_pk']
        )


class OrderProductDeliverViewSet(viewsets.ModelViewSet):
    """
    OrderProductDeliver ViewSet
    """
    serializer_class = s.OrderProductDeliverSerializer

    def get_queryset(self):
        return m.OrderProductDeliver.objects.filter(
            order_product__id=self.kwargs['orderproduct_pk']
        )
