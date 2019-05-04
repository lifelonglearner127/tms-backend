from rest_framework import viewsets, mixins, status
from rest_framework.response import Response

from ..core import constants
from ..core.permissions import IsAccountStaffOrReadOnly
from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAccountStaffOrReadOnly]

    def create(self, request):

        if request.user.role == constants.USER_ROLE_CUSTOMER:
            pass
        else:
            pass

        products = request.data.pop('products')
        loading_station = request.data.pop('loading_station')
        context = {
            'products': products,
            'loading_station': loading_station
        }

        serializer = self.serializer_class(
            data=request.data, context=context
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'results': serializer.data},
            status=status.HTTP_201_CREATED
        )
