from django.conf.urls import url, include
from django.urls import path

from rest_framework.routers import DefaultRouter
from .import views

router = DefaultRouter(trailing_slash=False)
router.register(
    r'products',
    views.ProductViewSet,
    base_name='products'
)
router.register(
    r'stations',
    views.StationViewSet,
    base_name='stations'
)

urlpatterns = [
    url(r'^', include(router.urls)),
    path('options/product-categories', views.ProductCategoriesView.as_view()),
]
