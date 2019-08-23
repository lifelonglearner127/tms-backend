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
    r'tires',
    v.TireViewSet,
    base_name='tires'
)
router.register(
    r'vehicle-maintenances',
    v.VehicleMaintenanceRequestViewSet,
    base_name='vehicle-maintenances'
)
router.register(
    r'vehicle-check-items',
    v.VehicleCheckItemViewSet,
    base_name='vehicle-check-items'
)
router.register(
    r'vehicle-check-history',
    v.VehicleCheckHistoryViewSet,
    base_name='vehicle-check-history'
)

urlpatterns = [
    url(r'^', include(router.urls)),
]
