from django.conf.urls import url, include
from rest_framework_nested import routers

from .import views as v

router = routers.SimpleRouter(trailing_slash=False)
router.register(
    r'user', v.UserViewSet, base_name='user'
)
router.register(
    r'customer', v.CustomerProfileViewSet, base_name='customer'
)
router.register(
    r'staff', v.StaffProfileViewSet, base_name='staff'
)
staff_router = routers.NestedSimpleRouter(
    router,
    r'staff',
    lookup='staff'
)
staff_router.register(
    r'documents',
    v.StaffDocumentViewSet,
    base_name='staff-documents'
)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(staff_router.urls)),
    url(r'^short/staff/$', v.ShortStaffAPIView.as_view()),
    url(r'^short/customer/$', v.ShortCustomerAPIView.as_view()),
    url(r'^options/document-type/$', v.UserDocumentTypeAPIView.as_view())
]
