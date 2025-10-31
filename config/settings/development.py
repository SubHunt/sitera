from .base import *

# Debug settings
DEBUG = True

# Database settings for development - using PostgreSQL
# DATABASES from base.py will be used (PostgreSQL)

# Additional apps for development
# INSTALLED_APPS += [
#     'django_debug_toolbar',
# ]

# Middleware for development
# MIDDLEWARE += [
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# ]

# Debug Toolbar settings
# INTERNAL_IPS = [
#     '127.0.0.1',
#     'localhost',
# ]

# Email settings for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Static files for development
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
