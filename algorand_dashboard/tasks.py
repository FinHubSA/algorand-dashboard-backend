from celery import shared_task
from .celery import app
from celery.utils.log import get_task_logger
from django.core.management import call_command

logger = get_task_logger(__name__)

@app.task
def seed_indexer_api():
    call_command("seed", )

@shared_task
def send_notification():
    print("Here I am")


