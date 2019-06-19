
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
# LANGUAGE_CODE = 'zh-hans'   # en-us
LANGUAGE_CODE = 'en-us'   # en-us
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
    'rest_framework_swagger',
    'corsheaders',
    'channels'
]
LOCAL_APPS = [
    'tms.account.apps.AccountConfig',
    'tms.info.apps.InfoConfig',
    'tms.core',
    'tms.order.apps.OrderConfig',
    'tms.vehicle.apps.VehicleConfig',
    'tms.job.apps.JobConfig',
    'tms.road.apps.RoadConfig',
    'tms.g7.apps.G7Config',
    'tms.notification.apps.NotificationConfig',
    'tms.hr.apps.HrConfig',
    'tms.finance.apps.FinanceConfig'
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# Middleware
# ----------------------------------------------------------------------------
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
if env.str('DATABASE_URL', default=''):
    DATABASES = {
        'default': env.db(),
    }
else:
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
BASE_DIR = str(ROOT_DIR)
STATIC_ROOT = str(ROOT_DIR("staticfiles"))
STATIC_URL = "/static/"
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# media
# ----------------------------------------------------------------------------
MEDIA_URL =  '/media/'
MEDIA_ROOT = str(ROOT_DIR("media"))


# Django Rest Framework
# ----------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'tms.account.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
    ),
    'DEFAULT_PAGINATION_CLASS':
        'tms.core.pagination.StandardResultsSetPagination',
}

JWT_AUTH = {
    'JWT_RESPONSE_PAYLOAD_HANDLER':
    'tms.account.views.jwt_response_payload_handler',
    'JWT_VERIFY_EXPIRATION': False
}


# G7 Settings
# ----------------------------------------------------------------------------
G7_HTTP_HOST = env.str('G7_HTTP_HOST')
G7_HTTP_BASEURL = env.str('G7_HTTP_BASEURL')
G7_HTTP_VEHICLE_BASIC_ACCESS_ID = env.str('G7_HTTP_VEHICLE_BASIC_ACCESS_ID')
G7_HTTP_VEHICLE_BASIC_SECRET = env.str('G7_HTTP_VEHICLE_BASIC_SECRET')
G7_HTTP_VEHICLE_DATA_ACCESS_ID = env.str('G7_HTTP_VEHICLE_DATA_ACCESS_ID')
G7_HTTP_VEHICLE_DATA_SECRET = env.str('G7_HTTP_VEHICLE_DATA_SECRET')

G7_MQTT_HOST = env.str('G7_MQTT_HOST')
G7_MQTT_POSITION_TOPIC = env.str('G7_MQTT_POSITION_TOPIC')
G7_MQTT_POSITION_CLIENT_ID = env.str('G7_MQTT_POSITION_CLIENT_ID')
G7_MQTT_POSITION_ACCESS_ID = env.str('G7_MQTT_POSITION_ACCESS_ID')
G7_MQTT_POSITION_SECRET = env.str('G7_MQTT_POSITION_SECRET')


# MapAPI Settings
# ----------------------------------------------------------------------------
MAP_WEB_SERVICE_API_KEY = env.str('MAP_WEB_SERVICE_API_KEY')


# Django Channels Settings
# ----------------------------------------------------------------------------
ASGI_APPLICATION = 'config.routing.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}