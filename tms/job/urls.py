from django.conf.urls import url, include
from rest_framework_nested import routers

from .import views as v

router = routers.SimpleRouter(trailing_slash=False)

# /jobs
# /jobs/{pk}
router.register(
    r'jobs', v.JobViewSet, base_name='job'
)
router.register(
    r'notifications', v.DriverNotificationViewSet, base_name='notification'
)

# /jobs/{job_pk}/missions
# /jobs/{job_pk}/missions/{pk}
job_router = routers.NestedSimpleRouter(
    router,
    r'jobs',
    lookup='job'
)
job_router.register(
    r'missions',
    v.MissionViewSet,
    base_name='missions'
)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(job_router.urls)),
]
