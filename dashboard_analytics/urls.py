from django.urls import re_path
from dashboard_analytics import views

urlpatterns = [
    re_path(r'^api/accounts$', views.account_list, name='account_list'),
    re_path(r'^api/node_transactions$', views.node_transactions, name='node_transactions'),
    re_path(r'^api/total_transactions$', views.total_transactions, name='total_transactions'),
    re_path(r'^api/total_volume$', views.total_volume, name='total_volume'),
    re_path(r'^api/most_active_addresses$', views.most_active_addresses, name='most_active_addresses'),
    re_path(r'^api/most_active_accounts$', views.most_active_accounts, name='most_active_accounts'),
    re_path(r'^api/account_type_payments_receipts$', views.account_type_payments_receipts, name='account_type_payments_receipts'),
    re_path(r'^api/account_type_total$', views.account_type_total, name='account_type_total'),
    re_path(r'^api/average_transaction_amount$', views.average_transaction_amount, name='average_transaction_amount'),
    re_path(r'^api/average_loan_amount$', views.average_loan_amount, name='average_loan_amount'),
    re_path(r'^api/account_type_transaction_volume$', views.account_type_transaction_volume, name='account_type_transaction_volume'),
]
