from rest_framework import viewsets, status
from rest_framework.response import Response

from ..core import constants
from ..core.permissions import IsAccountStaffOrReadOnly
from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    Order Viewset
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAccountStaffOrReadOnly]

    def create(self, request):
        if request.user.role == constants.USER_ROLE_CUSTOMER:
            pass
        else:
            pass

        assignee = request.data.pop('assignee')
        customer = request.data.pop('customer')
        products = request.data.pop('products')
        loading_station = request.data.pop('loading_station')
        context = {
            'assignee': assignee,
            'customer': customer,
            'products': products,
            'loading_station': loading_station
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
        if request.user.role == constants.USER_ROLE_CUSTOMER:
            pass
        else:
            pass

        assignee = request.data.pop('assignee')
        customer = request.data.pop('customer')
        products = request.data.pop('products')
        loading_station = request.data.pop('loading_station')
        context = {
            'assignee': assignee,
            'customer': customer,
            'products': products,
            'loading_station': loading_station
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
