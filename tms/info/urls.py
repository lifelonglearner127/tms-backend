from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from .import views

router = DefaultRouter(trailing_slash=False)
router.register(
    r'products', views.ProductViewSet, base_name='product'
)
router.register(
    r'place/load', views.LoadingStationViewSet, base_name='loading'
)
router.register(
    r'place/unload', views.UnLoadingStationViewSet, base_name='unloading'
)
router.register(
    r'place/quality', views.QualityStationViewSet, base_name='quality'
)
router.register(
    r'place/oil', views.OilStationViewSet, base_name='oil'
)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^product-categories/$', views.ProductCategoriesView.as_view()),
    url(r'^short/products/$', views.ShortProductView.as_view())
]
