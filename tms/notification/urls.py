from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter
from .import views

router = DefaultRouter(trailing_slash=False)
router.register(
    r'notifications',
    views.NotificationViewSet,
    base_name='notifications'
)
router.register(
    r'events',
    views.EventViewSets,
    base_name='events'
)
router.register(
    r'g7-mqtt-events',
    views.G7MQTTEventViewSets,
    base_name='g7-mqtt-events'
)


urlpatterns = [
    url(r'^', include(router.urls)),
]
