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
    r'fuel-consumptions',
    v.FuelConsumptionViewSet,
    base_name='fuel-consumptions'
)
router.register(
    r'vehicle-maintenances',
    v.VehicleMaintenanceRequestViewSet,
    base_name='vehicle-maintenances'
)

urlpatterns = [
    url(r'^', include(router.urls)),
]
