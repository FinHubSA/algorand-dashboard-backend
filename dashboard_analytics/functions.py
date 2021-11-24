import django
from django.conf import settings
from django.db import transaction, connection
from django.db.models import F
from datetime import datetime

from algosdk.v2client import indexer
import pandas as pd
from io import StringIO

INDEXER_CLIENT = indexer.IndexerClient(settings.INDEXER_TOKEN, settings.INDEXER_ADDRESS)

def retrieve_blockchain_data():

    print("retrieving data...")

    accounts_df = get_accounts_address_index()

    with connection.cursor() as cursor:
        # create temp table
        cursor.execute(
            'CREATE TEMP TABLE source AS SELECT * FROM dashboard_analytics_account LIMIT 0;')
        # copy_from from buffer to temp table
        copy_from_stringio(connection, accounts_df, 'source')
        # copy over and insert into old table from temp table
        cursor.execute(
            '''
                INSERT INTO dashboard_analytics_account ("Address","Balance","Name","AccountTypeID_id")
                SELECT "Address" ,"Balance", "Name", "AccountTypeID_id"
                FROM source
                ON CONFLICT ("Address") DO UPDATE
                SET "Balance" = EXCLUDED."Balance"
                '''
        )
        cursor.execute('DROP TABLE source')
    
    print("retrieved data")
    
def copy_from_stringio(conn, df, table):
    """
    Here we are going save the dataframe in memory 
    and use copy_from() to copy it to the table
    """
    # save dataframe to an in memory buffer
    buffer = StringIO()
    df.to_csv(buffer, index_label='Address', header=False)
    buffer.seek(0)

    cursor = conn.cursor()
    try:
        cursor.copy_from(buffer, table, sep=",")
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:

        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    print("copy_from_stringio() done")

def get_accounts_address_index():
    nexttoken = ""
    numtx = 1
    accounts_global = []
    # loop using next_page to paginate until there are no more transactions in the response
    # for the limit (max is 1000  per request)
    while (numtx > 0):
        response = INDEXER_CLIENT.accounts(limit=1000, next_page=nexttoken)
        accounts = pd.DataFrame(response['accounts'])

        if len(accounts.columns) == 0:
            break
        else:
            pass

        accounts = accounts[["address", "amount"]].set_index("address")
        accounts.columns = ['Balance']
        accounts['Name'] = "undefined"
        accounts['AccountTypeID_id'] = 1

        accounts.index.names = ['Address']
        accounts_global.append(accounts)
        numtx = len(accounts)
        if (numtx > 0):
            nexttoken = response['next-token']
    accounts_full = pd.concat(accounts_global, ignore_index=False)
    print(accounts_full)
    # convert balance to algos. 0.1 algos = 100000 micro aglos. balance currently in microalgos divide by 1000000
    accounts_full['Balance'] = accounts_full['Balance']/1000000
    accounts_full['Balance'] = accounts_full['Balance'].round(13)
    print(accounts_full)
    return accounts_full

@transaction.atomic
def process_json_transactions(transactions):
    from .models import AccountType, InstrumentType, Account, Transaction

    for txn in transactions:
        
        if not Transaction.objects.filter(TransactionID=txn["pk"]).exists():
            s_acctype_id = int(txn["fields"]["SenderAccountTypeCode"])
            r_acctype_id = int(txn["fields"]["ReceiverAccountTypeCode"])

            sender_account_type = AccountType.objects.get(AccountTypeID=s_acctype_id)
            receiver_account_type = AccountType.objects.get(AccountTypeID=r_acctype_id)

            if Account.objects.filter(Address=txn["fields"]["Sender"]).exists():
                Account.objects.filter(Address=txn["fields"]["Sender"]).update(Balance=F("Balance") - txn["fields"]["Amount"])
            else:
                Account.objects.create(
                    Address=txn["fields"]["Sender"],
                    AccountTypeID=sender_account_type,
                    Balance= -1 * txn["fields"]["Amount"])
            
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