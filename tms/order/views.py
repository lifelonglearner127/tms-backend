from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action

from . import models as m
from . import serializers as s
from ..info.models import Product
from ..info.serializers import ProductSerializer



class OrderViewSet(viewsets.ModelViewSet):
    """
    Order Viewset
    """
    queryset = m.Order.objects.all()
    serializer_class = s.OrderSerializer

    def create(self, request):
        context = {
            'assignee': request.data.pop('assignee'),
            'customer': request.data.pop('customer'),
            'products': request.data.pop('products'),
            'loading_station': request.data.pop('loading_station')
        }

        serializer = self.serializer_class(
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
            'assignee': request.data.pop('assignee'),
            'customer': request.data.pop('customer'),
            'products': request.data.pop('products'),
            'loading_station': request.data.pop('loading_station')
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


class OrderProductViewSet(viewsets.ModelViewSet):
    """
    OrderProduct Viewset
    """
    serializer_class = s.OrderProductSerializer

    def get_queryset(self):
        return m.OrderProduct.objects.filter(
            order__id=self.kwargs['order_pk']
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


class JobViewSet(viewsets.ModelViewSet):
    """
    Job Viewset
    """
    serializer_class = s.JobSerializer

    def get_queryset(self):
        return m.Job.objects.filter(
            mission__id=self.kwargs['mission_pk']
        )
