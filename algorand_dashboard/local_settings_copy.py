DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'algorand_dashboard',
        'USER': 'algorand_admin',
        'PASSWORD': '123456',
        'HOST': '127.0.0.1',
        'PORT': '5432'
    }
}

# redis settings
REDIS_HOST="localhost"
REDIS_PORT="6379"
# celery settings
CELERY_BROKER_URL = "redis://"+REDIS_HOST+":"+REDIS_PORT
CELERY_RESULT_BACKEND = "redis://"+REDIS_HOST+":"+REDIS_PORT
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
