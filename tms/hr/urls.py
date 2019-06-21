from django.conf.urls import url, include
from rest_framework_nested import routers

from . import views as v


router = routers.SimpleRouter(trailing_slash=False)
router.register(
    r'department',
    v.DepartmentViewSet,
    base_name='department'
)
router.register(
    r'position',
    v.PositionViewSet,
    base_name='position'
)
router.register(
    r'role-management',
    v.RoleManagementViewSet,
    base_name='role-management'
)
router.register(
    r'staff-profile',
    v.StaffProfileViewSet,
    base_name='staff-profile'
)
router.register(
    r'customer-profile',
    v.CustomerProfileViewSet,
    base_name='customer-profile'
)
router.register(
    r'rest-request',
    v.RestRequestViewSet,
    base_name='rest-request'
)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'options/rest-request-categories', v.RestRequestCategoriesView.as_view())
]
