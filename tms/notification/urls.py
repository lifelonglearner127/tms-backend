from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter
from .import views

router = DefaultRouter(trailing_slash=False)
router.register(
    r'notifications',
    views.NotificationViewSet,
    base_name='notifications'
)

urlpatterns = [
    url(r'^', include(router.urls)),
]
