from django.conf.urls import url
from dashboard_analytics import views

urlpatterns = [
    url(r'^api/accounts$', views.account_list, name='account_list'),
    url(r'^api/node_transactions$', views.node_transactions, name='node_transactions'),
    url(r'^api/total_transactions$', views.total_transactions, name='total_transactions'),
    url(r'^api/total_volume$', views.total_volume, name='total_volume'),
    url(r'^api/most_active_addresses$', views.most_active_addresses, name='most_active_addresses'),
    url(r'^api/most_active_accounts$', views.most_active_accounts, name='most_active_accounts'),
    url(r'^api/account_type_payments_receipts$', views.account_type_payments_receipts, name='account_type_payments_receipts'),
    url(r'^api/account_type_total$', views.account_type_total, name='account_type_total'),
    url(r'^api/average_transaction_amount$', views.average_transaction_amount, name='average_transaction_amount'),
    url(r'^api/average_loan_amount$', views.average_loan_amount, name='average_loan_amount'),
    url(r'^api/account_type_transaction_volume$', views.account_type_transaction_volume, name='account_type_transaction_volume'),
]
