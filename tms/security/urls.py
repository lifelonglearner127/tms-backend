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
router.register(
    r'questions',
    v.QuestionViewSet,
    base_name='questions'
)
router.register(
    r'security/tests',
    v.TestViewSet,
    base_name='tests'
)
router.register(
    r'security/programs',
    v.SecurityLearningProgramViewSet,
    base_name='programs'
)
router.register(
    r'security/libraries',
    v.SecurityLibraryViewSet,
    base_name='libraries'
)

# router.register(
#     r'security-knowledge',
#     v.SecurityKnowledgeViewSet,
#     base_name='security-knowledge'
# )

urlpatterns = [
    url(r'^', include(router.urls)),
    path('apps/company-policy/<int:policy_id>', v.get_company_policy, name='app-company-policy'),
    path('apps/tests/<int:test_id>/', v.get_test_template, name='app-test'),
    path('apps/tests/<int:test_id>/<int:question_id>/vote/', v.answer_question, name='answer-question'),
]
