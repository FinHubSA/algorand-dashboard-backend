from ctypes.wintypes import CHAR
from os import truncate
import django
import json
import base64
import psycopg2
import pandas as pd

from django.conf import settings
from django.db import transaction as db_transaction, connection
from django.db.models import Subquery, OuterRef, Case, When, Value, F, Q
from datetime import datetime
from dashboard_analytics.models import AccountType, InstrumentType, Account, Transaction
from datetime import datetime, timezone

from algosdk.v2client import indexer, algod
from algosdk import account, mnemonic, constants
from algosdk.future import transaction

# import pandas as pd
from io import StringIO

INDEXER_CLIENT = indexer.IndexerClient(settings.INDEXER_TOKEN, settings.INDEXER_ADDRESS)

def process_blockchain_accounts():

    print("retrieving accounts data...")

    accounts_df = get_accounts_address_index()

    with connection.cursor() as cursor:
        # create temp table
        cursor.execute(
            'CREATE TEMP TABLE source AS SELECT * FROM dashboard_analytics_account LIMIT 0;')
        # copy_from from buffer to temp table
        copy_from_stringio(connection, accounts_df, 'source','Address')
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
    
    print("retrieved accounts data")
    
def copy_from_stringio(conn, df, table, index_label):
    """
    Here we are going save the dataframe in memory 
    and use copy_from() to copy it to the table
    """
    # save dataframe to an in memory buffer
    buffer = StringIO()
    df.to_csv(buffer, sep="|", index_label=index_label, header=False)
    buffer.seek(0)

    print("*** string io ***")
    '''count = 0
    for sline in buffer.readlines():
        if (count < 1):
            print(sline)
        count = count + 1'''

    cursor = conn.cursor()
    try:
        cursor.copy_from(buffer, table, sep="|")
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
        accounts['AccountTypeID_id'] = 0

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


def process_blockchain_transactions():
    print("retrieving transactions data...")

    # get the latest transaction by RoundTime
    latest_transaction = Transaction.objects.latest('RoundTime')
    round_time = latest_transaction.RoundTime

    # print("*** round time *** ", round_time)
    transactions_df = get_blockchain_tansactions(round_time)

    with connection.cursor() as cursor:
        
        # create temp table
        cursor.execute(
            'CREATE TEMP TABLE source AS SELECT * FROM dashboard_analytics_transaction LIMIT 0;')
        
        # copy_from from buffer to temp table
        copy_from_stringio(connection, transactions_df, 'source', 'TransactionID')
        
        # copy over and insert into old table from temp table
        cursor.execute(
            '''
                INSERT INTO dashboard_analytics_transaction ("TransactionID","Timestamp","Amount","InstrumentTypeID_id","Receiver_id","Sender_id","RoundTime","ReceiverTypeId","SenderTypeId")
                SELECT "TransactionID","Timestamp","Amount","InstrumentTypeID_id","Receiver_id","Sender_id","RoundTime","ReceiverTypeId","SenderTypeId"
                FROM source
                '''
        )
        cursor.execute('DROP TABLE source')
    
    print("retrieved transaction data")

def get_blockchain_tansactions(round_time):
    nexttoken = ""
    numtx = 1

    start_time = datetime.fromtimestamp(round_time).astimezone(timezone.utc).isoformat('T')
    transactions_global = []

    # loop using next_page to paginate until there are no more transactions in the response
    # for the limit (max is 1000  per request)
    while (numtx > 0):
        response = INDEXER_CLIENT.search_transactions(start_time=start_time, next_page=nexttoken, limit=1000)
        transactions = pd.json_normalize(response['transactions'])

        if len(transactions.columns) == 0:
            break
        else:
            pass

        transactions = transactions[["id", "sender","payment-transaction.receiver","payment-transaction.amount","note","round-time"]].set_index('id')
        transactions['note'] = transactions['note'].apply(lambda x: base64.b64decode(x).decode())
        transactions = transactions[transactions['note'].str.contains(";")==True]
        print(transactions["note"])
        print(" *** txn length ***", len(transactions))
        transactions[['SenderType', 'ReceiverType', 'InstrumentTypeID', 'Timestamp']] = transactions['note'].str.split(";", expand=True, n=4)
        
        #transactions['TransactionID'] = transactions['id']
        transactions['Timestamp'] = pd.to_datetime(transactions['Timestamp'],format='%Y-%m-%d-%H%M')
        transactions['Amount'] = transactions['payment-transaction.amount'].astype(float)
        transactions['InstrumentTypeID_id'] = transactions['InstrumentTypeID'].astype(int)
        transactions['Receiver_id'] = transactions['payment-transaction.receiver'].astype(str)
        transactions['Sender_id'] = transactions['sender'].astype(str)
        transactions['RoundTime'] = transactions['round-time'].astype(int)
        transactions['ReceiverTypeId'] = transactions['ReceiverType'].astype(int)
        transactions['SenderTypeId'] = transactions['SenderType'].astype(int)

        transactions.index.names = ['TransactionID']

        transactions = transactions[['Timestamp','Amount','InstrumentTypeID_id','Receiver_id','Sender_id','RoundTime','ReceiverTypeId','SenderTypeId']]

        transactions_global.append(transactions)
        numtx = len(transactions)
        if (numtx > 0):
            nexttoken = response['next-token']
    transactions_full = pd.concat(transactions_global, ignore_index=False)
    # print(transactions_full)

    # print("*** columns 2 ***")
    # print(transactions_full.columns)

    return transactions_full

def create_blockchain_data(transactions):
    # data structures to keep already generated addresses
    chain_accounts = {}
    chain_keys = {}
    unsigned_transactions = []
    funding_transactions = []

    # print("*** 1 blockchain data ***")

    algod_client = algod.AlgodClient(settings.ALGOD_TOKEN, settings.ALGOD_ADDRESS)
    params = algod_client.suggested_params()
    funding_account_key = mnemonic.to_private_key(settings.ALGOD_FUNDING_MNEMONIC)

    # first check if the blockchain data has not been filled already
    funding_account_info = algod_client.account_info(settings.ALGOD_FUNDING_ADDRESS)
    # print("*** fund info ***",funding_account_info)

    # print("*** 2 blockchain data ***")
    # for each txn check if account is created already or add it
    for txn in transactions:
        sender_address = txn["fields"]["Sender"]
        receiver_address = txn["fields"]["Receiver"]

        # set the addresses if not set yet
        if (sender_address not in chain_accounts):
            private_key, address = account.generate_account()
            chain_accounts[sender_address] = [private_key, address]
            chain_keys[address] = private_key

            # fund the account
            funding_txn = transaction.PaymentTxn(settings.ALGOD_FUNDING_ADDRESS, params, address, 1000000000000, None, "funding transaction".encode())
            funding_transactions.append(funding_txn)

        if (receiver_address not in chain_accounts):
            private_key, address = account.generate_account()
            chain_accounts[receiver_address] = [private_key, address]
            chain_keys[address] = private_key

            # fund the account
            funding_txn = transaction.PaymentTxn(settings.ALGOD_FUNDING_ADDRESS, params, address, 1000000000000, None, "funding transaction".encode())
            funding_transactions.append(funding_txn)

        # get the chain adresses
        sender_chain_address = chain_accounts[sender_address][1]
        receiver_chain_address = chain_accounts[receiver_address][1]

        # sender private key
        sender_private_key = chain_accounts[sender_address][0]

        # build transaction
        note = txn["fields"]["SenderAccountTypeCode"]+";"+txn["fields"]["ReceiverAccountTypeCode"]+";"+txn["fields"]["InstrumentTypeCode"]+";"+txn["fields"]["Timestamp"]
        note = note.encode()

        amount = int(txn["fields"]["Amount"] * 1000000)
        unsigned_txn = transaction.PaymentTxn(sender_chain_address, params, receiver_chain_address, amount, None, note)
        unsigned_transactions.append(unsigned_txn)

    create_blockchain_transactions(algod_client, funding_transactions, funding_account_key, None)
    create_blockchain_transactions(algod_client, unsigned_transactions, None, chain_keys)

def create_blockchain_transactions(algod_client, transactions, funding_account_key, chain_keys):

    # max group size is 16 so send them in 16s
    start_index = 0
    last_index = min(start_index + 16, len(transactions))

    initial_pending_transactions_number = len(algod_client.pending_transactions(0))

    # print("*** initial pending transactions ***", initial_pending_transactions_number)

    # print("*** start txn processing ***")

    while start_index < len(transactions):
        
        signed_transaction_group = []

        transaction_group = transactions[start_index:last_index]
        transaction.assign_group_id(transaction_group)

        # print("*** state: l: "+str(len(transactions))+" i: "+str(start_index)+" - "+str(last_index)+" g: "+str(len(transaction_group)))

        for un_txn in transaction_group:
            if (funding_account_key is None):
                sender_key = chain_keys[un_txn.sender]
                signed_transaction_group.append(un_txn.sign(sender_key))
            else:
                signed_transaction_group.append(un_txn.sign(funding_account_key))

        #increment the indexes 
        start_index = last_index
        last_index = min(start_index + 16, len(transactions))

        # submit transactions 
        # print("*** txn 0 ***", transaction_group[0])
        try:
            txid = algod_client.send_transactions(signed_transaction_group)
        except Exception as err:
            print("*** err 1 ***", err)
            continue
    
    pending_transactions_number = initial_pending_transactions_number + 1
    while pending_transactions_number > initial_pending_transactions_number:
        try:
            pending_transactions = algod_client.pending_transactions(0)
            pending_transactions_number = len(pending_transactions)
            print("*** pending transactions ***", " pending: "+str(pending_transactions_number)+" initial: "+str(initial_pending_transactions_number))
        except Exception as err:
            print("*** err 1 ***", err)
            continue

def process_accounts_info():
    """
    This function will populate the account type if its not populated already
    """

    print("populating account type information...")

    # print("*** account info ***")
    Account.objects.filter(
        AccountTypeID = 0
    ).annotate(
        Txn_AccountTypeID = Subquery(
            Transaction.objects.filter(
                Q(Sender = OuterRef('Address')) | Q(Receiver = OuterRef('Address'))
            ).annotate(
                account_type= Case (
                    When(Sender=OuterRef('Address'), then=F('ReceiverTypeId')),
                    When(Receiver=OuterRef('Address'), then=F('ReceiverTypeId')),
                    default=0
                )
            ).values('account_type')[:1]
        )
    ).update(AccountTypeID = Case (
        When(Txn_AccountTypeID__isnull=True, then=0),
        default=F('Txn_AccountTypeID')
    ))

    print("populating account type information successful!")

@db_transaction.atomic
def process_json_data(transactions):
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