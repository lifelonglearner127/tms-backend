from .base import *  # noqa
from .base import env
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


# Generals
# ----------------------------------------------------------------------------
DEBUG = True
SECRET_KEY = env("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]
CORS_ORIGIN_WHITELIST = [
    'http://localhost:8080',
    'http://localhost:8081'
]

# Sentry Settings
# ----------------------------------------------------------------------------
sentry_sdk.init(
    dsn="https://a5ae3c6beaa24e76bcdd0f87a9aa0371@sentry.io/1488082",
    integrations=[DjangoIntegration()]
)
