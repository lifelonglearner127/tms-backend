from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

# models
from . import models as m

# serializers
from . import serializers as s

# views
from ..core.views import TMSViewSet


class ETCCardViewSet(TMSViewSet):

    queryset = m.ETCCard.objects.all()
    serializer_class = s.ETCCardSerializer
    short_serializer_class = s.ETCCardNumberSerializer

    def get_queryset(self):
        queryset = self.queryset
        card_type = self.request.query_params.get('type', None)
        if card_type == 'master':
            queryset = queryset.filter(is_child=False)
        elif card_type == 'child':
            queryset = queryset.filter(is_child=True)

        return queryset

    def create(self, request):
        context = {
            'master': request.data.pop('master'),
            'vehicle': request.data.pop('vehicle'),
            'department': request.data.pop('department')
        }
        serializer = s.ETCCardSerializer(
            data=request.data, context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        instance = self.get_object()
        context = {
            'master': request.data.pop('master'),
            'vehicle': request.data.pop('vehicle'),
            'department': request.data.pop('department')
        }
        serializer = s.ETCCardSerializer(
            instance, data=request.data, context=context, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, url_path="master")
    def get_master_cards(self, request):
        serializer = s.ETCCardNumberSerializer(
            self.queryset.filter(is_child=False), many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], url_path='charge')
    def charge_card(self, request, pk=None):
        card = self.get_object()
        current_balance = card.balance
        charged_amount = float(request.data.get('charged_amount', 0))
        m.ETCCardChargeHistory.objects.create(
            card=card,
            previous_amount=current_balance,
            charged_amount=charged_amount,
            after_amount=current_balance + charged_amount,
            charged_on=timezone.now()
        )
        card.balance += charged_amount
        card.save()

        if card.is_child:
            card.master.balance -= charged_amount
            card.master.save()

        return Response(
            s.ETCCardSerializer(card).data,
            status=status.HTTP_200_OK
        )


class ETCCardChargeHistoryViewSet(TMSViewSet):

    queryset = m.ETCCardChargeHistory.objects.all()
    serializer_class = s.ETCCardChargeHistorySerializer


class ETCBillHistoryViewSet(TMSViewSet):

    queryset = m.ETCBillHistory.objects.all()
    serializer_class = s.ETCBillHistorySerializer

    def create(self, request):
        context = {
            'user': request.user,
            'images': request.data.pop('images'),
            'request': request
        }
        serializer = self.serializer_class(
            data=request.data, context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FuelCardViewSet(TMSViewSet):

    queryset = m.FuelCard.objects.all()
    short_serializer_class = s.FuelCardNumberSerializer
    serializer_class = s.FuelCardSerializer

    def get_queryset(self):
        queryset = self.queryset
        card_type = self.request.query_params.get('type', None)
        if card_type == 'master':
            queryset = queryset.filter(is_child=False)
        elif card_type == 'child':
            queryset = queryset.filter(is_child=True)

        return queryset

    def create(self, request):
        context = {
            'master': request.data.pop('master'),
            'vehicle': request.data.pop('vehicle'),
            'department': request.data.pop('department')
        }
        serializer = s.FuelCardSerializer(
            data=request.data, context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        instance = self.get_object()
        context = {
            'master': request.data.pop('master'),
            'vehicle': request.data.pop('vehicle'),
            'department': request.data.pop('department')
        }
        serializer = s.FuelCardSerializer(
            instance, data=request.data, context=context, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, url_path="master")
    def get_master_cards(self, request):
        serializer = s.FuelCardNumberSerializer(
            self.queryset.filter(is_child=False), many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], url_path='charge')
    def charge_card(self, request, pk=None):
        card = self.get_object()
        current_balance = card.balance
        charged_amount = float(request.data.get('charged_amount', 0))
        m.FuelCardChargeHistory.objects.create(
            card=card,
            previous_amount=current_balance,
            charged_amount=charged_amount,
            after_amount=current_balance + charged_amount,
            charged_on=timezone.now()
        )
        card.balance += charged_amount
        card.save()

        if card.is_child:
            card.master.balance -= charged_amount
            card.master.save()

        return Response(
            s.FuelCardSerializer(card).data,
            status=status.HTTP_200_OK
        )


class FuelCardChargeHistoryViewSet(TMSViewSet):

    queryset = m.FuelCardChargeHistory.objects.all()
    serializer_class = s.FuelCardChargeHistorySerializer


class FuelBillHistoryViewSet(TMSViewSet):

    queryset = m.FuelBillHistory.objects.all()
    serializer_class = s.FuelBillHistorySerializer

    def create(self, request):
        context = {
            'user': request.user,
            'images': request.data.pop('images'),
            'request': request
        }
        serializer = self.serializer_class(
            data=request.data, context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


# class BillDocumentViewSet(TMSViewSet):

#     queryset = m.BillDocument.objects.all()
#     serializer_class = s.BillDocumentSerializer

#     def create(self, request):
#         user_id = request.data.pop('user', None)
#         if user_id is None:
#             user = request.user
#         else:
#             user = get_object_or_404(User, pk=user_id)

#         serializer = s.BillDocumentSerializer(
#             data=request.data,
#             context={'user': user, 'request': request}
#         )

#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return Response(
#             serializer.data,
#             status=status.HTTP_201_CREATED
#         )

#     def update(self, request, pk=None):
#         instance = self.get_object()
#         user_id = request.data.pop('user', None)
#         if user_id is None:
#             user = request.user
#         else:
#             user = User.objects.get(pk=user_id)

#         serializer = s.BillDocumentSerializer(
#             instance,
#             data=request.data,
#             context={'user': user, 'request': request}
#         )

#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK
#         )

#     @action(detail=False, url_path='my-bills')
#     def get_my_bills(self, request):
#         category = request.query_params.get('category', None)

#         if category is not None:
#             page = self.paginate_queryset(
#                 request.user.bills.filter(category=category),
#             )
#         else:
#             page = self.paginate_queryset(
#                 request.user.bills.all(),
#             )

#         serializer = s.BillDocumentSerializer(
#             page,
#             context={'request': request},
#             many=True
#         )

#         return self.get_paginated_response(serializer.data)

#     @action(detail=True, url_path='my-bills')
#     def get_my_bill(self, request, pk=None):
#         bill = get_object_or_404(m.BillDocument, user=request.user, pk=pk)
#         serializer = s.BillDocumentSerializer(
#             bill,
#             context={'request': request}
#         )

#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK
#         )


class BillViewSet(TMSViewSet):

    queryset = m.Bill.objects.all()
    serializer_class = s.BillSerializer

    def create(self, request):
        context = {
            'user': request.user,
            'images': request.data.pop('images'),
            'request': request
        }
        serializer = self.serializer_class(
            data=request.data, context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        instance = self.get_object()
        context = {
            'user': request.user,
            'images': request.data.pop('images'),
            'request': request
        }
        serializer = self.serializer_class(
            instance, data=request.data, context=context, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
