from django.conf.urls import url, include
from rest_framework_nested import routers

from .import views as v

router = routers.SimpleRouter(trailing_slash=False)

router.register(
    r'parking-request',
    v.ParkingRequestViewSet,
    base_name='parking-request'
)
router.register(
    r'driver-change-request',
    v.DriverChangeRequestViewSet,
    base_name='driver-change'
)
router.register(
    r'escort-change-request',
    v.EscortChangeRequestViewSet,
    base_name='escort-change'
)
router.register(
    r'rest-request',
    v.RestRequestViewSet,
    base_name='rest-request'
)

# # /jobs/{job_pk}/missions
# # /jobs/{job_pk}/missions/{pk}
# job_router = routers.NestedSimpleRouter(
#     router,
#     r'jobs',
#     lookup='job'
# )
# job_router.register(
#     r'missions',
#     v.MissionViewSet,
#     base_name='missions'
# )

urlpatterns = [
    url(r'^', include(router.urls)),
    # url(r'^', include(job_router.urls)),
]
