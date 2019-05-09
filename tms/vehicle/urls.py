from django.conf.urls import url, include
from rest_framework_nested import routers

from .import views as v

router = routers.SimpleRouter(trailing_slash=False)
router.register(
    r'vehicle', v.VehicleViewSet, base_name='vehicle'
)
vehicle_router = routers.NestedSimpleRouter(
    router,
    r'vehicle',
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
    url(r'^vehicle-brand/$', v.VehicleBrandAPIView.as_view()),
    url(r'^vehicle-model/$', v.VehicleModelAPIView.as_view()),
]
