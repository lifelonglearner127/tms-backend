
"""
Base settings to build other settings upon
"""

import environ

ROOT_DIR = (environ.Path(__file__) - 3)
APPS_DIR = ROOT_DIR.path("tms")

env = environ.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    env.read_env(str(ROOT_DIR.path(".env")))


# Generals
# ----------------------------------------------------------------------------
DEBUG = env.bool("DJANGO_DEBUG", False)
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
SITE_ID = 1


# Apps
# ----------------------------------------------------------------------------
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders'
]
LOCAL_APPS = [
    'tms.account',
    'tms.info',
    'tms.core',
    'tms.order',
    'tms.vehicle'
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# Middleware
# ----------------------------------------------------------------------------
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# Authentication
# ----------------------------------------------------------------------------
AUTH_USER_MODEL = 'account.User'
AUTHENTICATION_BACKENDS = [
    'tms.account.backends.TMSAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend'
]


# Urls
# ----------------------------------------------------------------------------
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'


# Templates
# ----------------------------------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# Database
# ----------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(ROOT_DIR.path('db.sqlite3')),
    },
}

# Password Validation
# ----------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Static
# ----------------------------------------------------------------------------
STATIC_URL = '/static/'


# Django Rest Framework
# ----------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
    ),
    'DEFAULT_PAGINATION_CLASS': 'tms.core.pagination.StandardResultsSetPagination',
}

JWT_AUTH = {
    'JWT_RESPONSE_PAYLOAD_HANDLER':
    'tms.account.views.jwt_response_payload_handler',
    'JWT_VERIFY_EXPIRATION': False
}

CORS_ORIGIN_WHITELIST = [
    'http://localhost:8080'
]


# OpenAPI Settings
# ----------------------------------------------------------------------------
G7SANDBOX = env.bool("G7SANDBOX", False)

if G7SANDBOX:
    OPENAPI_HOST = 'http://demo.dsp.chinawayltd.com'
    OPENAPI_BASEURL = '/altair/rest'
    OPENAPI_VEHICLE_BASIC_ACCESS_ID = 'vt8hc8'
    OPENAPI_VEHICLE_BASIC_SECRET = 'Vstn1zquSry4b18DwkmeOY6pQUuPa0vn'
    OPENAPI_VEHICLE_DATA_ACCESS_ID = 'd3un7m'
    OPENAPI_VEHICLE_DATA_SECRET = 'XohiKSlObj70BIQ3nF3achF6n2gaCaeU'
else:
    OPENAPI_HOST = 'http://openapi.huoyunren.com'
    OPENAPI_BASEURL = ''
    OPENAPI_VEHICLE_BASIC_ACCESS_ID = 'jxnwrs'
    OPENAPI_VEHICLE_BASIC_SECRET = 'W2Hxj0mC5Yc1b19mZJGb8wD4QW6D3Rgt'
    OPENAPI_VEHICLE_DATA_ACCESS_ID = 'jxnwrs'
    OPENAPI_VEHICLE_DATA_SECRET = 'W2Hxj0mC5Yc1b19mZJGb8wD4QW6D3Rgt'
