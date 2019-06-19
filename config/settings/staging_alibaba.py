from .base import *  # noqa
from .base import env


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
