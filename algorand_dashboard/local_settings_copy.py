DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'algorand_dashboard',
        'USER': 'algorand_admin',
        'PASSWORD': '123456',
        'HOST': '127.0.0.1', # 'db'  # for docker
        'PORT': '5432'
    }
}

# redis settings
REDIS_HOST="localhost" # "redis" # for docker
REDIS_PORT="6379"

# celery settings
CELERY_BROKER_URL = "redis://"+REDIS_HOST+":"+REDIS_PORT
CELERY_RESULT_BACKEND = "redis://"+REDIS_HOST+":"+REDIS_PORT
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# Algorand Blockchain Connection Settings
ALGOD_ADDRESS = "http://localhost:4001" # http://host.docker.internal:4001" # for docker
ALGOD_TOKEN = "a" * 64
INDEXER_ADDRESS = "http://localhost:8980" # "http://host.docker.internal:8980" # for docker
INDEXER_TOKEN = ALGOD_TOKEN
ALGOD_FUNDING_ADDRESS = "HVSTYAQWRQNIBZVXXHHTRT2MVOG54P5UHRFLM5OYT7BDXFOMZAUCQ6UY5E"
ALGOD_FUNDING_MNEMONIC = "material wrist treat noodle spare fresh health kite gallery sock size ridge travel rose route crime water oak scrap conduct pledge diamond mixture abandon will"

# If set to true the json or blockchain data tasks will automatically start when server starts
AUTO_POPULATE = False
# This parameter is to determine whether to use blockchain or json data
USE_BLOCKCHAIN_DATA = False
