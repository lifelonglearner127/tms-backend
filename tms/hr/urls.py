from django.conf.urls import url, include
from rest_framework_nested import routers

from . import views as v


router = routers.SimpleRouter(trailing_slash=False)
router.register(
    r'rest-request',
    v.RestRequestViewSet,
    base_name='rest-request'
)

urlpatterns = [
    url(r'^', include(router.urls)),
]
