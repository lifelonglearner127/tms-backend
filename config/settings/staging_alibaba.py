from .base import *  # noqa
from .base import env
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


# General
# ----------------------------------------------------------------------------
SECRET_KEY = env("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = [
    '*'
]

CORS_ORIGIN_WHITELIST = [
    'http://47.98.111.251',
    'https://47.98.111.251'
]

# Sentry Settings
# ----------------------------------------------------------------------------
sentry_sdk.init(
    dsn="https://a5ae3c6beaa24e76bcdd0f87a9aa0371@sentry.io/1488082",
    integrations=[DjangoIntegration()]
)
