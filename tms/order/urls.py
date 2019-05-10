from django.conf.urls import url, include
from django.urls import path
from rest_framework_nested import routers

from .import views as v

router = routers.SimpleRouter(trailing_slash=False)

# /orders
# /orders/{pk}
router.register(
    r'orders', v.OrderViewSet, base_name='order'
)

# /orders/{order_pk}/products
# /orders/{order_pk}/products/{pk}
order_router = routers.NestedSimpleRouter(
    router,
    r'orders',
    lookup='order'
)
order_router.register(
    r'products',
    v.OrderProductViewSet,
    base_name='ordered-products'
)

# /orders/{order_pk}/products/{product_pk}/delivers
# /orders/{order_pk}/products/{product_pk}/delivers/{pk}
orderproduct_router = routers.NestedSimpleRouter(
    order_router,
    r'products',
    lookup='orderproduct'
)
orderproduct_router.register(
    r'delivers',
    v.OrderProductDeliverViewSet,
    base_name='ordered-product-delivers'
)

# /orders/{order_pk}/products/{product_pk}/delivers/{deliver_pk}/jobs
# /orders/{order_pk}/products/{product_pk}/delivers/{deliver_pk}/jobs/{pk}
deliever_router = routers.NestedSimpleRouter(
    orderproduct_router,
    r'delivers',
    lookup='mission'
)
deliever_router.register(
    r'jobs',
    v.JobViewSet,
    base_name='jobs'
)
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(order_router.urls)),
    url(r'^', include(orderproduct_router.urls)),
    url(r'^', include(deliever_router.urls)),
]
