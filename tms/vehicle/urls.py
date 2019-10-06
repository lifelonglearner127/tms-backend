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
    r'vehicle-check-items',
    v.VehicleCheckItemViewSet,
    base_name='vehicle-check-items'
)
router.register(
    r'vehicle-check-history',
    v.VehicleCheckHistoryViewSet,
    base_name='vehicle-check-history'
)
router.register(
    r'vehicle-maintenance-history',
    v.VehicleMaintenanceHistoryViewSet,
    base_name='vehicle-maintenance-history'
)
router.register(
    r'vehicle-tires',
    v.VehicleTireViewSet,
    base_name='vehicle-tires'
)
router.register(
    r'vehicle-tires-change-history',
    v.TireManagementHistoryViewSet,
    base_name='vehicle-tires'
)
router.register(
    r'vehicle-binds',
    v.VehicleDriverEscortBindViewSet,
    base_name='vehicle-user-binds'
)
urlpatterns = [
    url(r'^', include(router.urls)),
]
