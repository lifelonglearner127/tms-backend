from django.conf.urls import url, include
from rest_framework_nested import routers

from . import views as v


router = routers.SimpleRouter(trailing_slash=False)
router.register(
    r'order-payment',
    v.OrderPaymentViewSet,
    base_name='order-payment'
)
router.register(
    r'etc-card',
    v.ETCCardViewSet,
    base_name='etc-card'
)
router.register(
    r'etc-charges',
    v.ETCCardChargeHistoryViewSet,
    base_name='etc-charges'
)
router.register(
    r'etc-usages',
    v.ETCCardUsageHistoryViewSet,
    base_name='etc-usages'
)
router.register(
    r'fuel-card',
    v.FuelCardViewSet,
    base_name='fuel-card'
)
router.register(
    r'bill',
    v.BillDocumentViewSet,
    base_name='bill'
)

urlpatterns = [
    url(r'^', include(router.urls)),
]
