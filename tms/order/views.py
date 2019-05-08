from rest_framework import viewsets, status
from rest_framework.response import Response

from . import models as m
from . import serializers as s


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
