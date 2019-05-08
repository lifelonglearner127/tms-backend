from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from .import views as v

router = DefaultRouter(trailing_slash=False)
router.register(
    r'user', v.UserViewSet, base_name='user'
)
router.register(
    r'profile', v.StaffProfileViewSet, base_name='profile'
)
router.register(
    r'customer', v.CustomerViewSet, base_name='customer'
)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^short/staff/$', v.ShortStaffAPIView.as_view()),
    url(r'^short/customer/$', v.ShortCustomerAPIView.as_view())
]
