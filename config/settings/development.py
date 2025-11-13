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
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Для отладки
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Для реальной отправки
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Настройки SMTP сервера
EMAIL_HOST = config('EMAIL_HOST', default='mail.sitera.kz')
EMAIL_PORT = config('EMAIL_PORT', default=25, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)

# Настройки аутентификации
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Настройки отправителя
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='info@sitera.kz')
SERVER_EMAIL = config('SERVER_EMAIL', default='info@sitera.kz')

# Получатели уведомлений
NOTIFICATION_EMAIL = config('NOTIFICATION_EMAIL', default='info@sitera.kz')

# Static files for development
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
