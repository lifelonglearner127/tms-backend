from django.conf.urls import url, include
from rest_framework_nested import routers

from .import views as v

router = routers.SimpleRouter(trailing_slash=False)

# /orders
# /orders/{pk}
router.register(
    r'orders', v.OrderViewSet, base_name='order'
)

# /orders/{order_pk}/loading-stations
# /orders/{order_pk}/loading-stations/{pk}
order_router = routers.NestedSimpleRouter(
    router,
    r'orders',
    lookup='order'
)
order_router.register(
    r'loading-stations',
    v.OrderLoadingStationViewSet,
    base_name='order-loading-stations'
)

# /orders/{order_pk}/loading-stations/{orderloadingstation_pk}/products
# /orders/{order_pk}/loading-stations/{orderloadingstation_pk}/products/{pk}
orderloadingstation_router = routers.NestedSimpleRouter(
    order_router,
    r'loading-stations',
    lookup='orderloadingstation'
)
orderloadingstation_router.register(
    r'products',
    v.OrderProductViewSet,
    base_name='order-loadingstations'
)

# /orders/{order_pk}/loading-stations/{orderloadingstation_pk}/products/delivers
# /orders/{order_pk}/loading-stations/{orderloadingstation_pk}/products/delivers/{pk}
orderproduct_router = routers.NestedSimpleRouter(
    orderloadingstation_router,
    r'products',
    lookup='orderproduct'
)
orderproduct_router.register(
    r'delivers',
    v.OrderProductDeliverViewSet,
    base_name='delivers'
)
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(order_router.urls)),
    url(r'^', include(orderloadingstation_router.urls)),
    url(r'^', include(orderproduct_router.urls)),
]
