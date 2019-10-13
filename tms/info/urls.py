from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter
from .import views as v

router = DefaultRouter(trailing_slash=False)
router.register(
    r'products',
    v.ProductViewSet,
    base_name='products'
)
router.register(
    r'stations',
    v.StationViewSet,
    base_name='stations'
)
router.register(
    r'transportation-distance',
    v.TransportationDistanceViewSet,
    base_name='transportation-distance'
)

router.register(
    r'other-cost-types',
    v.OtherCostTypeViewSet,
    base_name='other-cost-types'
)

router.register(
    r'ticket-types',
    v.TicketTypeViewSet,
    base_name='ticket-types'
)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'basic-setting', v.BasicSettingAPIView.as_view()),
    url(r'tax-setting', v.TaxRateAPIView.as_view()),
]
