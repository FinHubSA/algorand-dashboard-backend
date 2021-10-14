import os

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "algorand_dashboard.settings")

app = Celery("algorand_dashboard", include=['algorand_dashboard.tasks'])
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
