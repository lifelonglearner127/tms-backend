from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from .import views

router = DefaultRouter(trailing_slash=False)
router.register(
    r'user', views.UserViewSet, base_name='user'
)
router.register(
    r'customer', views.CustomerViewSet, base_name='customer'
)

urlpatterns = [
    url(r'^', include(router.urls)),
]
