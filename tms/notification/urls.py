from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter
from .import views

router = DefaultRouter(trailing_slash=False)
router.register(
    r'driver/job/notifcations',
    views.DriverJobNotificationViewSet,
    base_name='driver-job-notifications'
)

urlpatterns = [
    url(r'^', include(router.urls)),
]
