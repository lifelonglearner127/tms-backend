from django.conf.urls import url, include

from rest_framework_nested import routers

from .import views as v

router = routers.SimpleRouter(trailing_slash=False)
router.register(
    r'vehicles',
    v.VehicleViewSet,
    base_name='vehicle'
)
router.register(
    r'vehicle-maintenances',
    v.VehicleMaintenanceRequestViewSet,
    base_name='vehicle-maintenances'
)
router.register(
    r'vehicle-binds',
    v.VehicleUserBindViewSet,
    base_name='vehicle-user-binds'
)
urlpatterns = [
    url(r'^', include(router.urls)),
]
