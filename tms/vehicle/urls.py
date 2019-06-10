from django.conf.urls import url, include
from django.urls import path

from rest_framework_nested import routers

from .import views as v

router = routers.SimpleRouter(trailing_slash=False)
router.register(
    r'vehicles', v.VehicleViewSet, base_name='vehicle'
)
urlpatterns = [
    url(r'^', include(router.urls)),
    path('options/vehicle-brand', v.VehicleBrandAPIView.as_view()),
    path('options/vehicle-model', v.VehicleModelAPIView.as_view()),
]
