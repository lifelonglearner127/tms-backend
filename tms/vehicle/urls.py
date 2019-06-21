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
urlpatterns = [
    url(r'^', include(router.urls)),
    url(
        r'options/vehicle-brand',
        v.VehicleBrandAPIView.as_view()
    ),
    url(
        r'options/vehicle-model',
        v.VehicleModelAPIView.as_view()
    ),
    url(
        r'options/vehicle-maintenance-categories',
        v.VehicleMaintenanceRequestCategoriesAPIView.as_view()
    )
]
