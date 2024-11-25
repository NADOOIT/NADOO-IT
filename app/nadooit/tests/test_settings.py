"""
Test settings for dependency compatibility tests
"""
from nadooit.settings import *

import os
import sys

# Add the app directory to the Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

# Debug settings
DEBUG = False
INTERNAL_IPS = []
ALLOWED_HOSTS = ['*']

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static-files/'  # Changed to be more specific
MEDIA_URL = '/media-files/'    # Changed to be completely different

# Configure storage backends
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Configure directories
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'test_media')

# Create directories if they don't exist
os.makedirs(STATIC_ROOT, exist_ok=True)
os.makedirs(MEDIA_ROOT, exist_ok=True)

# Basic installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'nadooit',
    'nadooit_auth',
    'nadooit_website',
]

# Auth settings
AUTH_USER_MODEL = 'nadooit_auth.User'

# Security settings
SECRET_KEY = 'test-key-not-for-production'

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Templates
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

# URL configuration for tests
ROOT_URLCONF = 'nadooit.tests.test_urls'

# Static files configuration
STATICFILES_DIRS = []

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Security settings for tests
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_USE_SESSIONS = True

# Celery settings for tests
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache'
CELERY_CACHE_BACKEND = 'memory'

# OpenAI settings for tests
OPENAI_API_KEY = 'dummy_key'

# Create test data for Section_Order
SECTION_ORDER_TEST_DATA = True

# Disable debug toolbar completely
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: False,
    'DISABLE_PANELS': {'debug_toolbar.panels.redirects.RedirectsPanel'},
    'SHOW_TEMPLATE_CONTEXT': False,
    'ENABLE_STACKTRACES': False,
}
