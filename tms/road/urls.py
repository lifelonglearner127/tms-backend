from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from .import views as v

router = DefaultRouter(trailing_slash=False)
router.register(
    r'routes',
    v.RouteViewSet,
    base_name='route'
)

router.register(
    r'points',
    v.PointViewSet,
    base_name='path'
)

urlpatterns = [
    url(r'^', include(router.urls)),
]
