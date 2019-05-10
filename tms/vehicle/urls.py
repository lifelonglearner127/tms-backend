from django.conf.urls import url, include
from django.urls import path

from rest_framework_nested import routers

from .import views as v

router = routers.SimpleRouter(trailing_slash=False)
router.register(
    r'vehicles', v.VehicleViewSet, base_name='vehicle'
)
vehicle_router = routers.NestedSimpleRouter(
    router,
    r'vehicles',
    lookup='vehicle'
)
vehicle_router.register(
    r'documents',
    v.VehicleDocumentViewSet,
    base_name='vehicle-documents'
)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(vehicle_router.urls)),
    path('options/vehicle-brand', v.VehicleBrandAPIView.as_view()),
    path('options/vehicle-model', v.VehicleModelAPIView.as_view()),
]
