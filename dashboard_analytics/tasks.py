from django.conf import settings
from celery import shared_task
from celery.utils.log import get_task_logger
from .data.cbdc_dict import data
import inspect
import redis

# Connect to our Redis instance
redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,port=settings.REDIS_PORT, db=0)

@shared_task
def process_transactions_task():
    from .functions import process_json_transactions
    # Check if task has run yet
    # Get the function name
    task_name = inspect.stack()[0][3]

    if not redis_instance.exists(task_name):
        print("Executing Task: "+task_name)
        redis_instance.set(task_name, "")
        
        # Process transactions
        process_json_transactions(data)
        
        print("Finished Task: "+task_name)
        redis_instance.delete(task_name)
    


