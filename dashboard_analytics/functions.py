import django
from django.db import transaction
from django.db.models import F
from datetime import datetime

@transaction.atomic
def process_json_transactions(transactions):
    from .models import AccountType, InstrumentType, Account, Transaction

    for txn in transactions:
        # print(txn["pk"])
        if not Transaction.objects.filter(TransactionID=txn["pk"]).exists():
            s_acctype_id = int(txn["fields"]["SenderAccountTypeCode"])
            r_acctype_id = int(txn["fields"]["ReceiverAccountTypeCode"])

            sender_account_type = AccountType.objects.get(AccountTypeID=s_acctype_id)
            receiver_account_type = AccountType.objects.get(AccountTypeID=r_acctype_id)

            if not Account.objects.filter(Address=txn["fields"]["Sender"]).exists():
                Account.objects.create(
                    Address=txn["fields"]["Sender"],
                    AccountTypeID=sender_account_type,
                    Balance=0)
            
            if Account.objects.filter(Address=txn["fields"]["Receiver"]).exists():
                Account.objects.filter(Address=txn["fields"]["Receiver"]).update(Balance=F("Balance") + txn["fields"]["Amount"])
            else:
                Account.objects.create(
                    Address=txn["fields"]["Receiver"],
                    AccountTypeID=receiver_account_type,
                    Balance=txn["fields"]["Amount"])

            i_type_id = int(txn["fields"]["InstrumentTypeCode"])

            sender_account = Account.objects.get(Address=txn["fields"]["Sender"])
            receiver_account = Account.objects.get(Address=txn["fields"]["Receiver"])
            instrument_type = InstrumentType.objects.get(InstrumentTypeID=i_type_id)

            #2020-12-31-1200
            time_stamp_obj = datetime.strptime(txn["fields"]["Timestamp"], "%Y-%m-%d-%H%M")
            time_stamp_str = time_stamp_obj.strftime('%Y-%m-%d')

            Transaction.objects.create(
                TransactionID=txn["pk"],
                Sender=sender_account,
                Receiver=receiver_account,
                Amount=txn["fields"]["Amount"],
                # The InstrumentTypeCode from the json data is the InstrumentTypeID
                # The InstrumentTypeCode is human readable and not more than 2 letters
                InstrumentTypeID=instrument_type,
                Timestamp=time_stamp_str)