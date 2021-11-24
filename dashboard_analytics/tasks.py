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

    # Calls retrieve_blockchain_data_task() every 10 seconds.
    sender.add_periodic_task(10.0, retrieve_blockchain_data_task.s(), name='retrieve_blockchain_data_task')

    # process json transactions for test data
    process_transactions_task.delay()

@celery_app.task
def retrieve_blockchain_data_task():
    from .functions import retrieve_blockchain_data

    # Retrieve blockchain data
    retrieve_blockchain_data()


@celery_app.task
def process_transactions_task():
    from .functions import process_json_transactions

    # Process transactions
    process_json_transactions(data)
    


