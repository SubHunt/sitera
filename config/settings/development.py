from .base import *

# Debug settings
DEBUG = True

# Database settings for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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
