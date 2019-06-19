from django.conf.urls import url, include
from django.urls import path

from rest_framework_nested import routers

from .import views as v

router = routers.SimpleRouter(trailing_slash=False)
router.register(
    r'users', v.UserViewSet, base_name='user'
)

urlpatterns = [
    url(r'^', include(router.urls)),
    path('auth/obtain_token', v.ObtainJWTAPIView.as_view()),
    path('auth/verify_token', v.VerifyJWTAPIView.as_view()),
]
