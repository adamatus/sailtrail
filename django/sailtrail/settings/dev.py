"""
Django settings for sailtrail project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
# flake8: noqa
from .common import *

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIA_ROOT = os.path.join(BASE_DIR, '../../../uploads')
MEDIA_URL = '/media/'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATES[0]['OPTIONS']['debug'] = True

ALLOWED_HOSTS = []

# Application definition

# LiveReload needs to go before 'django.contrib.staticfiles'
INSTALLED_APPS = ('livereload',) + INSTALLED_APPS

INSTALLED_APPS += (
    'debug_toolbar',
)

MIDDLEWARE_CLASSES.insert(
    1,
    'debug_toolbar.middleware.DebugToolbarMiddleware'
)
MIDDLEWARE_CLASSES += [
    'livereload.middleware.LiveReloadScript',
    # 'qinspect.middleware.QueryInspectMiddleware',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, '../../../database/db.sqlite3'),
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(BASE_DIR, '../../../logs/email')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'qinspect': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

QUERY_INSPECT_ENABLED = True
QUERY_INSPECT_LOG_QUERIES = True
QUERY_INSPECT_LOG_TRACEBACKS = True
