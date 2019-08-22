from django.conf.urls import url, include
from rest_framework_nested import routers

from .import views as v

router = routers.SimpleRouter(trailing_slash=False)

# router.register(
#     r'parking-request',
#     v.ParkingRequestViewSet,
#     base_name='parking-request'
# )
# router.register(
#     r'driver-change-request',
#     v.DriverChangeRequestViewSet,
#     base_name='driver-change'
# )
# router.register(
#     r'escort-change-request',
#     v.EscortChangeRequestViewSet,
#     base_name='escort-change'
# )
router.register(
    r'requests',
    v.BasicRequestViewSet,
    base_name='requests'
)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'rest-request/categories', v.RestRequestCateogryAPIView.as_view()),
    url(r'vehicle-repair-request/categories', v.VehicleRepairRequestCategoryAPIView.as_view()),
]
