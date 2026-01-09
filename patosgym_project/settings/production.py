"""
Production settings for patosgym_project.
"""
from .base import *
from decouple import config

# Override DEBUG
DEBUG = False

# ALLOWED_HOSTS from environment
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='patosgym.com.ar,www.patosgym.com.ar').split(',')

# CSRF Settings
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='https://patosgym.com.ar,https://www.patosgym.com.ar'
).split(',')

# Security settings for production
SECURE_SSL_REDIRECT = False  # Nginx maneja SSL
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Database - override if using DATABASE_URL
if config('DATABASE_URL', default=None):
    import dj_database_url
    DATABASES['default'] = dj_database_url.parse(config('DATABASE_URL'))

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
