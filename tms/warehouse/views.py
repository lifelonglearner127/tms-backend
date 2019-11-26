from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response
from drf_renderer_xlsx.mixins import XLSXFileMixin
from drf_renderer_xlsx.renderers import XLSXRenderer

from ..core import constants as c
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


class InTransactionHistoryViewSet(XLSXFileMixin, TMSViewSet):

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


class InTransactionHistoryExportViewSet(XLSXFileMixin, viewsets.ReadOnlyModelViewSet):

    queryset = m.InTransaction.objects.all()
    serializer_class = s.InTransactionHistoryExportSerializer
    pagination_class = None
    renderer_classes = (XLSXRenderer, )
    filename = 'export.xlsx'
    body = c.EXCEL_BODY_STYLE

    def get_column_header(self):
        ret = c.EXCEL_HEAD_STYLE
        ret['titles'] = [
            '名称', '发票类型', '单价', '数量', '数量单位', '供货商', '供货商联系人', '联系人电话', '日期',
        ]
        return ret


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


class OutTransactionHistoryExportViewSet(XLSXFileMixin, viewsets.ReadOnlyModelViewSet):

    queryset = m.OutTransaction.objects.all()
    serializer_class = s.OutTransactionHistoryExportSerializer
    pagination_class = None
    renderer_classes = (XLSXRenderer, )
    filename = 'export.xlsx'
    body = c.EXCEL_BODY_STYLE

    def get_column_header(self):
        ret = c.EXCEL_HEAD_STYLE
        ret['titles'] = [
            '名称', '领取人', '单价', '数量', '数量单位', '日期', '车牌号', '发票类型',
        ]
        return ret
