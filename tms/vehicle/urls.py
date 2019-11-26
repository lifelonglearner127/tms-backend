from django.conf.urls import url, include
from django.urls import path

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
    r'vehicle-violations',
    v.VehicleViolationViewSet,
    base_name='vehicle-violations'
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
    r'vehicle-tires-tread-depth-history',
    v.TireTreadDepthCheckHistoryViewSet,
    base_name='vehicle-tread-history'
)
router.register(
    r'vehicle-binds',
    v.VehicleDriverEscortBindViewSet,
    base_name='vehicle-user-binds'
)
router.register(
    r'export/tire-changes-history',
    v.VehicleTireChangeHistoryExportViewSet,
    base_name='export-tire-change-history'
)
router.register(
    r'export/tread-check-history',
    v.VehicleTireTreadCheckHistoryExportViewSet,
    base_name='export-tire-tread-check-history'
)
router.register(
    r'export-vehicle-tires',
    v.VehicleTireExportViewSet,
    base_name='export-vehicle-tires'
)

urlpatterns = [
    url(r'^', include(router.urls)),
    path('vehicle-violations/upload-csv/', v.VehicleViolationUploadView.as_view()),
    path('vehicle-maintenance/categories', v.VehicleMaintenanceCategoryAPIView.as_view()),
]
