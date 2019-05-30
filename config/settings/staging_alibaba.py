from .base import *  # noqa
from .base import env


# General
# ----------------------------------------------------------------------------
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="i1t=60pmfy@f2yloh#mzj7%)#jtgll(3wb@@@23w=l(ai&!q1%",
)
ALLOWED_HOSTS = [
    '0.0.0.0'
]

CORS_ORIGIN_WHITELIST = [
    'http://47.98.111.251',
    'https://47.98.111.251'
]
