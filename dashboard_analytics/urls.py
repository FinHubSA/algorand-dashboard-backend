from django.conf.urls import url
from dashboard_analytics import views

urlpatterns = [
    url(r'^api/accounts$', views.account_list),
    url(r'^api/node_transactions$', views.node_transactions),
    url(r'^api/total_transactions$', views.total_transactions),
    url(r'^api/total_volume$', views.total_volume),
    url(r'^api/most_active_addresses$', views.most_active_addresses),
    url(r'^api/account_type_total$', views.account_type_total),
]
