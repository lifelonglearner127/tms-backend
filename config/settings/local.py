from .base import *  # noqa
from .base import env

# Generals
# ----------------------------------------------------------------------------
DEBUG = True
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="i1t=60pmfy@f2yloh#mzj7%)#jtgll(3wb@@@23w=l(ai&!q1%",
)
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]
