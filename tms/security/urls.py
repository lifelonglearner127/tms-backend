from django.conf.urls import url, include
from django.urls import path

from rest_framework.routers import DefaultRouter
from .import views as v

router = DefaultRouter(trailing_slash=False)
router.register(
    r'company-policy',
    v.CompanyPolicyViewSet,
    base_name='company-policy'
)
# router.register(
#     r'security-knowledge',
#     v.SecurityKnowledgeViewSet,
#     base_name='security-knowledge'
# )

urlpatterns = [
    url(r'^', include(router.urls)),
    path('apps/company-policy/<int:policy_id>', v.get_company_policy, name='app-company-policy'),
]
