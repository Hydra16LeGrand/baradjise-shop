"""
Django settings for Baradji project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9hdg(=cnla^6sgfzu=tg0y3$@imae$3*l-^#izkovehc%7t859'

# SECURITY WARNING: don't run with debug turned on in production!
if os.environ.get('ENV') == 'PRODUCTION':
    DEBUG = False
else:
    DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',

    # 'storages',
    # 'gdstorage',

    'Client',
]

# SESSION_ENGINE = "django.contrib.sessions.backends.cache"
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'whitenoise.middleware.WhiteNoiseMiddleware',

]

ROOT_URLCONF = 'Baradji.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

WSGI_APPLICATION = 'Baradji.wsgi.application'

#Configuration google django-googledrive-storage
# GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE = 'sustained-pod-306722-dff1955920ba.json'
# GOOGLE_DRIVE_STORAGE_MEDIA_ROOT = os.path.join(BASE_DIR, 'media/') # OPTIONAL

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }

    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'baradji',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',
        'PORT': '',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'fr'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST_USER = 'baradjis.eshop@gmail.com'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_PASSWORD = "Ba-18021998"
EMAIL_USE_SSL = False





if os.environ.get('ENV') == 'PRODUCTION':

    # AWS_ACCESS_KEY_ID = 'AKIAIZRT3NRB36TDTOBA'
    # AWS_SECRET_ACCESS_KEY = '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'
    # AWS_STORAGE_BUCKET_NAME = 'baradjiseshop'

    # DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    # STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
    # AWS_S3_FILE_OVERWRITE = False
    # AWS_DEFAULT_ACL = None

    # Static files settings
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

    # Extra places for collectstatic to find static files.
    STATICFILES_DIRS = (
        os.path.join(BASE_DIR, 'static'),
    )

    # STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

    db_from_env = dj_database_url.config(conn_max_age=500)
    DATABASES['default'].update(db_from_env)

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                 'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
            },
        },
    }    