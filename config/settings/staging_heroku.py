import os
import django_heroku

from .base import *  # noqa
from .base import env


# General
# ----------------------------------------------------------------------------
SECRET_KEY = env("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = [
    'https://tms-heroku.herokuapp.com',
    'https://tms-frontend-heroku.herokuapp.com'
]

CORS_ORIGIN_WHITELIST = [
    'https://tms-heroku.herokuapp.com',
    'https://tms-frontend-heroku.herokuapp.com'
]

os.makedirs(str(APPS_DIR.path("static")), exist_ok=True)    # noqa
django_heroku.settings(locals())
