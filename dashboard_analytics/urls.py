from django.conf.urls import url
from dashboard_analytics import views

urlpatterns = [
    url(r'^api/dashboard$', views.account_list)
]
