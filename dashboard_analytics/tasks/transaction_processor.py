from dashboard_analytics.models import AccountType, InstrumentType, Account, Transaction

def process_json_transactions(transactions):
    for txn in transactions:
        print(txn["pk"])