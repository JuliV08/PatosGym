"""
Development settings for patosgym_project.
"""
from .base import *

# Override DEBUG
DEBUG = True

# ALLOWED_HOSTS for development
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'adjunctly-unemitted-braiden.ngrok-free.dev']

# Use SQLite for local development (simpler than PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# No SSL redirect in development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
