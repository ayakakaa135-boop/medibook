"""
MediBook - Modern Django Settings with i18n, HTMX, and Performance Optimization
"""
import os
from pathlib import Path
from decouple import config, Csv
import dj_database_url
import sys


BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
# Security
SECRET_KEY = config('SECRET_KEY', default='dev-secret-key-CHANGE-ME-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# Application definition
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third-party apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'compressor',
    'django_htmx',
    'widget_tweaks',
    'modeltranslation',
    'rosetta',
    'django_celery_beat',
    'apps.users',
    'apps.clinics',
    'apps.doctors',
    'apps.services',
    'apps.appointments',
    'apps.dashboard',
]

if DEBUG:
    INSTALLED_APPS += ['debug_toolbar', 'django_extensions']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # i18n
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

if DEBUG:
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'sslmode': 'require', # ضروري للاتصال بـ Supabase
        }
    }
}
# Cache (Redis)
"""
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',

            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
        'KEY_PREFIX': 'medibook',
        'TIMEOUT': 300,
    }
}
"""


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
# Session
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'ar'  # Default to Arabic
TIME_ZONE = "UTC"

USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('ar', 'العربية'),
    ('en', 'English'),
]

LOCALE_PATHS = [BASE_DIR / 'locale']

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

# Compression
COMPRESS_ENABLED = not DEBUG
COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter']
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

# WhiteNoise
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Custom user model
AUTH_USER_MODEL = 'users.User'
# أضف هذه الأسطر أسفل إعدادات Allauth الموجودة لديك
ACCOUNT_USERNAME_REQUIRED = False          # لا تطلب اسم مستخدم عند التسجيل
ACCOUNT_USER_MODEL_USERNAME_FIELD = None   # أخبر allauth أن الموديل لا يحتوي على حقل username أصلاً
ACCOUNT_AUTHENTICATION_METHOD = 'email'    # التأكيد على أن تسجيل الدخول بالإيميل فقط
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Allauth settings
SITE_ID = 1
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'optional'
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

# Celery Configuration
CELERY_BROKER_URL = config('REDIS_URL', default='redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://127.0.0.1:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Debug Toolbar
INTERNAL_IPS = ['127.0.0.1', 'localhost']

# Security settings (for production)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# Payment Gateway Settings
PAYMENT_GATEWAY = 'stripe'  # أو 'paytabs', 'checkout', إلخ

# Stripe Settings (مثال)
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
#STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

# Payment Settings
CANCELLATION_FEE_PERCENTAGE =os.getenv('CANCELLATION_FEE_PERCENTAGE') # 50% من السعر
LATE_PAYMENT_FEE_PERCENTAGE = os.getenv('LATE_PAYMENT_FEE_PERCENTAGE ')  # 5% كل أسبوع
MAX_LATE_FEE_PERCENTAGE = os.getenv('MAX_LATE_FEE_PERCENTAGE')   # حد أقصى 50%
PAYMENT_DUE_DAYS = os.getenv('PAYMENT_DUE_DAYS ')   # 25 يوم للدفع
# Currency
DEFAULT_CURRENCY =os.getenv('DEFAULT_CURRENCY')

# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER") 
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")  # App Password من Gmail
DEFAULT_FROM_EMAIL = 'mediabook@gmail.com'
