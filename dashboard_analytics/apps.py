from django.apps import AppConfig
from dashboard_analytics.tasks import process_transactions_task
# from dashboard_analytics.models import AccountType, InstrumentType, Account, Transaction

class DashboardAnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard_analytics'

    def ready(self):
        # print("im ready")
        process_transactions_task.delay()
