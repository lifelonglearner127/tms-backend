from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models as m
from . import serializers as s
from ..core.views import TMSViewSet
from ..account.models import User


class OrderPaymentViewSet(TMSViewSet):

    queryset = m.OrderPayment.objects.all()
    serializer_class = s.OrderPaymentSerializer
    data_view_serializer_class = s.OrderPaymentDataViewSerializer


class ETCCardViewSet(TMSViewSet):

    queryset = m.ETCCard.objects.all()
    serializer_class = s.ETCCardSerializer
    short_serializer_class = s.ShortETCCardSerializer


class ETCCardChargeHistoryViewSet(TMSViewSet):

    queryset = m.ETCCardChargeHistory.objects.all()
    serializer_class = s.ETCCardChargeHistorySerializer


class ETCCardUsageHistoryViewSet(TMSViewSet):

    queryset = m.ETCCardUsageHistory.objects.all()
    serializer_class = s.ETCCardUsageHistorySerializer


class FuelCardViewSet(TMSViewSet):

    queryset = m.FuelCard.objects.all()
    short_serializer_class = s.ShortFuelCardSerializer
    serializer_class = s.FuelCardSerializer

    def create(self, request):
        pass

    def update(self, request, pk=None):
        pass


class BillDocumentViewSet(TMSViewSet):

    queryset = m.BillDocument.objects.all()
    serializer_class = s.BillDocumentSerializer

    def create(self, request):
        user_id = request.data.pop('user', None)
        if user_id is None:
            user = request.user
        else:
            user = get_object_or_404(User, pk=user_id)

        serializer = s.BillDocumentSerializer(
            data=request.data,
            context={'user': user, 'request': request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        user_id = request.data.pop('user', None)
        if user_id is None:
            user = request.user
        else:
            user = User.objects.get(pk=user_id)

        serializer = s.BillDocumentSerializer(
            instance,
            data=request.data,
            context={'user': user, 'request': request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='my-bills')
    def get_my_bills(self, request):
        category = request.query_params.get('category', None)

        if category is not None:
            page = self.paginate_queryset(
                request.user.bills.filter(category=category),
            )
        else:
            page = self.paginate_queryset(
                request.user.bills.all(),
            )

        serializer = s.BillDocumentSerializer(
            page,
            context={'request': request},
            many=True
        )

        return self.get_paginated_response(serializer.data)

    @action(detail=True, url_path='my-bills')
    def get_my_bill(self, request, pk=None):
        bill = get_object_or_404(m.BillDocument, user=request.user, pk=pk)
        serializer = s.BillDocumentSerializer(
            bill,
            context={'request': request}
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
