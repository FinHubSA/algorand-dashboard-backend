from django.apps import AppConfig
# from dashboard_analytics.tasks import process_json_data_task

class DashboardAnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard_analytics'

    def ready(self):
        print("dashboard_analytics apps ready")
        # process_json_data_task.delay()
