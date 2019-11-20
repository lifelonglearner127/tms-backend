from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

# models
from . import models as m

# serializers
from . import serializers as s

# views
from ..core.views import TMSViewSet


class WarehouseProductViewSet(TMSViewSet):

    queryset = m.WarehouseProduct.objects.all()
    serializer_class = s.WarehouseProductSerializer

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset

    def create(self, request):
        assignee = request.data.pop('assignee', None)

        serializer = s.WarehouseProductSerializer(
            data=request.data,
            context={
                'assignee': assignee
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
        assignee = request.data.pop('assignee', None)

        serializer = s.WarehouseProductSerializer(
            instance,
            data=request.data,
            context={
                'assignee': assignee
            }
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class InTransactionHistoryViewSet(TMSViewSet):

    queryset = m.InTransaction.objects.all()
    serializer_class = s.InTransactionSerializer

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(product__name__icontains=name)

        return queryset


class InTransactionViewSet(TMSViewSet):

    serializer_class = s.InTransactionSerializer

    def get_queryset(self):
        return m.InTransaction.objects.filter(
            product__id=self.kwargs['product_pk']
        )

    def create(self, request, product_pk=None):
        product = get_object_or_404(m.WarehouseProduct, id=product_pk)
        serializer = s.InTransactionSerializer(
            data=request.data,
            context={
                'product': product
            }
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def update(self, request, product_pk=None, pk=None):
        product = get_object_or_404(m.WarehouseProduct, id=product_pk)
        instance = self.get_object()
        serializer = s.InTransactionSerializer(
            instance,
            data=request.data,
            context={
                'product': product
            }
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class OutTransactionHistoryViewSet(TMSViewSet):

    queryset = m.OutTransaction.objects.all()
    serializer_class = s.OutTransactionSerializer

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(product__name__icontains=name)

        return queryset


class OutTransactionViewSet(TMSViewSet):

    serializer_class = s.OutTransactionSerializer

    def get_queryset(self):
        return m.OutTransaction.objects.filter(
            product__id=self.kwargs['product_pk']
        )

    def create(self, request, product_pk=None):
        product = get_object_or_404(m.WarehouseProduct, id=product_pk)
        serializer = s.OutTransactionSerializer(
            data=request.data,
            context={
                'product': product,
                'recipient': request.data.pop('recipient')
            }
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def update(self, request, product_pk=None, pk=None):
        product = get_object_or_404(m.WarehouseProduct, id=product_pk)
        instance = self.get_object()
        serializer = s.OutTransactionSerializer(
            instance,
            data=request.data,
            context={
                'product': product,
                'recipient': request.data.pop('recipient')
            }
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
