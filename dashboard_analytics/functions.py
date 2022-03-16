import django
import json
import pandas as pd

from django.conf import settings
from django.db import transaction as db_transaction, connection
from django.db.models import F
from datetime import datetime

from algosdk.v2client import indexer, algod
from algosdk import account, mnemonic, constants
from algosdk.future import transaction


# import pandas as pd
from io import StringIO

INDEXER_CLIENT = indexer.IndexerClient(settings.INDEXER_TOKEN, settings.INDEXER_ADDRESS)

def process_blockchain_data():

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

@db_transaction.atomic
def create_blockchain_data(transactions):
    # data structures to keep already generated addresses
    chain_accounts = {}
    chain_keys = {}
    unsigned_transactions = []
    funding_transactions = []

    print("*** 1 blockchain data ***")

    algod_client = algod.AlgodClient(settings.ALGOD_TOKEN, settings.ALGOD_ADDRESS)
    params = algod_client.suggested_params()
    funding_account_key = mnemonic.to_private_key(settings.ALGOD_FUNDING_MNEMONIC)

    # first check if the blockchain data has not been filled already
    funding_account_info = algod_client.account_info(settings.ALGOD_FUNDING_ADDRESS)
    print("*** fund info ***",funding_account_info)


    print("*** 2 blockchain data ***")
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
            funding_txn = transaction.PaymentTxn(settings.ALGOD_FUNDING_ADDRESS, params, address, 1000000000, None, "funding transaction")
            funding_transactions.append(funding_txn)

        if (receiver_address not in chain_accounts):
            private_key, address = account.generate_account()
            chain_accounts[receiver_address] = [private_key, address]
            chain_keys[address] = private_key

            # fund the account
            funding_txn = transaction.PaymentTxn(settings.ALGOD_FUNDING_ADDRESS, params, address, 1000000000, None, "funding transaction")
            funding_transactions.append(funding_txn)

        # get the chain adresses
        sender_chain_address = chain_accounts[sender_address][1]
        receiver_chain_address = chain_accounts[receiver_address][1]

        # sender private key
        sender_private_key = chain_accounts[sender_address][0]

        # build transaction
        note = txn["fields"]["SenderAccountTypeCode"]+";"+txn["fields"]["ReceiverAccountTypeCode"]+";"+txn["fields"]["InstrumentTypeCode"]

        amount = int(txn["fields"]["Amount"])
        unsigned_txn = transaction.PaymentTxn(sender_chain_address, params, receiver_chain_address, amount, None, note)
        unsigned_transactions.append(unsigned_txn)

    create_blockchain_transactions(algod_client, funding_transactions, funding_account_key, None)
    create_blockchain_transactions(algod_client, unsigned_transactions, None, chain_keys)

def create_blockchain_transaction(algod_client, transactions, funding_account_key, chain_keys):
    counter = 0
    for un_txn in transactions:
        print("*** state: l: "+str(len(transactions))+" i: "+str(counter)+" ***")

        if (funding_account_key is None):
            sender_key = chain_keys[un_txn.sender]
            signed_txn = un_txn.sign(sender_key)
        else:
            signed_txn = un_txn.sign(funding_account_key)

        counter = counter + 1

        try:
            txid = algod_client.send_transaction(signed_txn)
        except Exception as err:
            print("*** err 1 ***", err)
            continue
        
        print("*** submit blockchain data ***")
        # wait for confirmation 
        try:
            confirmed_txn = transaction.wait_for_confirmation(algod_client, txid, 4)
            print("Transaction Information: {}".format(json.dumps(confirmed_txn, indent=4)))
        except Exception as err:
            print("*** err 2 ***", err)
            continue


def create_blockchain_transactions(algod_client, transactions, funding_account_key, chain_keys):

    # max group size is 16 so send them in 16s
    start_index = 0
    last_index = min(start_index + 16, len(transactions))

    initial_pending_transactions_number = len(algod_client.pending_transactions(0))

    print("*** initial pending transactions ***", initial_pending_transactions_number)

    print("*** start txn processing ***")

    while start_index < len(transactions):
        
        signed_transaction_group = []

        transaction_group = transactions[start_index:last_index]
        transaction.assign_group_id(transaction_group)

        print("*** state: l: "+str(len(transactions))+" i: "+str(start_index)+" - "+str(last_index)+" g: "+str(len(transaction_group)))

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
        print("*** txn 0 ***", transaction_group[0])
        try:
            txid = algod_client.send_transactions(signed_transaction_group)
        except Exception as err:
            print("*** err 1 ***", err)
            continue

        print("*** submit blockchain data ***")
        # wait for confirmation 
        """ try:
            confirmed_txn = transaction.wait_for_confirmation(algod_client, txid, 4)
            print("Transaction Information: {}".format(json.dumps(confirmed_txn, indent=4)))
        except Exception as err:
            print("*** err 2 ***", err)
            continue """
    
    pending_transactions_number = initial_pending_transactions_number + 1
    while pending_transactions_number > initial_pending_transactions_number:
        try:
            pending_transactions = algod_client.pending_transactions(0)
            pending_transactions_number = len(pending_transactions)
            print("*** pending transactions ***", " pending: "+str(pending_transactions_number)+" initial: "+str(initial_pending_transactions_number))
        except Exception as err:
            print("*** err 1 ***", err)
            continue
        

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