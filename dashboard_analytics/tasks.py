from django.conf import settings
from celery import shared_task
from celery.utils.log import get_task_logger
from algorand_dashboard.celery import app as celery_app
from .data.cbdc_dict import data

import inspect
import redis

# Connect to our Redis instance
redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,port=settings.REDIS_PORT, db=0)

@celery_app.on_after_finalize.connect
def setup_tasks(sender, **kwargs):

    if (not settings.AUTO_POPULATE):
        return

    print("*** setup tasks! ***")
    if (not settings.USE_BLOCKCHAIN_DATA):
        print("*** 1 json ***")
        process_json_data_task.delay()
    else:
        print("*** 1 blockchain ***")
        create_blockchain_data_task.delay()

@celery_app.task
def create_blockchain_data_task():
    from .functions import create_blockchain_data

    print("*** 1 create blockchain data ***")
    # Create blockchain data
    create_blockchain_data(data)

@celery_app.task
def process_blockchain_data_task():
    from .functions import process_blockchain_data

    # Retrieve blockchain data
    process_blockchain_data()

@celery_app.task
def process_json_data_task():
    from .functions import process_json_data

    print("*** 2 json ***")
    # Process transactions
    process_json_data(data)
    


