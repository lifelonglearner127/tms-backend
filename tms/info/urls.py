from django.conf.urls import url, include
from django.urls import path

from rest_framework.routers import DefaultRouter
from .import views

router = DefaultRouter(trailing_slash=False)
router.register(
    r'products', views.ProductViewSet, base_name='products'
)
router.register(
    r'loading-stations',
    views.LoadingStationViewSet,
    base_name='loading-stations'
)
router.register(
    r'unloading-stations',
    views.UnLoadingStationViewSet,
    base_name='unloading-stations'
)
router.register(
    r'quality-stations',
    views.QualityStationViewSet,
    base_name='quality-stations'
)
router.register(
    r'oil-stations',
    views.OilStationViewSet,
    base_name='oil-stations'
)

urlpatterns = [
    url(r'^', include(router.urls)),
    path('options/product-categories', views.ProductCategoriesView.as_view()),
]
