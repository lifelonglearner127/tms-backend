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
    r'product-categories',
    v.ProductCategoryViewSet,
    base_name='product-categories'
)
router.register(
    r'stations',
    v.StationViewSet,
    base_name='stations'
)

router.register(
    r'routes',
    v.RouteViewSet,
    base_name='route'
)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'alarm-setting', v.AlarmSettingAPIView.as_view()),
]
