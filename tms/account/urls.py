from django.conf.urls import url, include
from django.urls import path

from rest_framework_nested import routers

from .import views as v

router = routers.SimpleRouter(trailing_slash=False)
router.register(
    r'users', v.UserViewSet, base_name='user'
)
router.register(
    r'customers', v.CustomerProfileViewSet, base_name='customer'
)
router.register(
    r'staffs', v.StaffProfileViewSet, base_name='staff'
)
router.register(
    r'drivers', v.DriverProfileViewSet, base_name='driver'
)
router.register(
    r'escorts', v.EscortProfileViewSet, base_name='escort'
)
staff_router = routers.NestedSimpleRouter(
    router,
    r'staffs',
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
    path('auth/obtain_token', v.ObtainJWTAPIView.as_view()),
    path('auth/verify_token', v.VerifyJWTAPIView.as_view()),
    path('options/document-type', v.UserDocumentTypeAPIView.as_view())
]
