from django.conf.urls import url, include
from rest_framework_nested import routers

from .import views as v

router = routers.SimpleRouter(trailing_slash=False)

# /orders
# /orders/{pk}
router.register(
    r'orders', v.OrderViewSet, base_name='order'
)
router.register(
    r'cart', v.OrderCartViewSet, base_name='order-cart'
)
router.register(
    r'jobs', v.JobViewSet, base_name='job'
)
router.register(
    r'job-report', v.JobReportViewSet, base_name='job-report'
)
router.register(
    r'order-report', v.OrderReportViewSet, base_name='order-report'
)
router.register(
    r'vehicle-binds', v.VehicleUserBindViewSet, base_name='vehicle-user-binds'
)

# # /jobs/{job_pk}/stations
# # /jobs/{job_pk}/stations/{pk}
job_router = routers.NestedSimpleRouter(
    router,
    r'jobs',
    lookup='job'
)
job_router.register(
    r'stations',
    v.JobStationViewSet,
    base_name='job-stations'
)

# /jobs/{job_pk}/stations/{jobstation_pk}/products
# /jobs/{job_pk}/stations/{jobstation_pk}/products/{pk}
jobstation_router = routers.NestedSimpleRouter(
    job_router,
    r'stations',
    lookup='job_station'
)
jobstation_router.register(
    r'products',
    v.JobStationProductViewSet,
    base_name='job-station-products'
)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(job_router.urls)),
    url(r'^', include(jobstation_router.urls)),
]
