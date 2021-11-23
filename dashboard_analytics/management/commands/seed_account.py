import psycopg2
from django.core.management.base import BaseCommand, CommandError
#import requests
from dashboard_analytics.models import AccountType, InstrumentType, Account, Transaction

# file to indexer API and save into postgres database
# Indexer port configuration
from algosdk.v2client import indexer
import pandas as pd
from io import StringIO

# indexer api connection
ALGOD_ADDRESS = "http://localhost:4001"
ALGOD_TOKEN = "a" * 64
INDEXER_ADDRESS = "http://localhost:8980"
INDEXER_TOKEN = ALGOD_TOKEN

INDEXER_CLIENT = indexer.IndexerClient(INDEXER_TOKEN, INDEXER_ADDRESS)

# database local connection - takunda to change
param_dic = {
    "host": "localhost",
    "database": "algodashboard",
    "user": "postgres",
    "password": "alli1510",
    "port": "5433"
}


def connect(params_dic):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params_dic)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        sys.exit(1)
    print("Connection successful")
    return conn


# accounts collection from api
def get_accounts_address_index():
    nexttoken = ""
    numtx = 1
    accounts_global = []
    # loop using next_page to paginate until there are no more transactions in the response
    # for the limit (max is 1000  per request)
    while (numtx > 0):
        response = INDEXER_CLIENT.accounts(
            limit=1000, next_page=nexttoken)
        accounts = pd.DataFrame(response['accounts'])
        if len(accounts.columns) == 0:
            break
        else:
            pass

        accounts = accounts[["address", "amount"]].set_index("address")
        accounts.columns = ['Balance']
        accounts['Name'] = "undefined"
        accounts['AccountTypeID_id'] = 6

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

# copy over buffer into table


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

# main function


def accounts_upload():
    try:
        # connect to database
        conn = connect(param_dic)
        # initialise cursor
        cursor = conn.cursor()
        # get accounts from API
        accounts_index_address = get_accounts_address_index()
        # create temp table
        cursor.execute(
            'CREATE TEMP TABLE source AS SELECT * FROM dashboard_analytics_account LIMIT 0;')
        # copy_from from buffer to temp table
        copy_from_stringio(conn, accounts_index_address, 'source')
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
        conn.commit()
        conn.close()
        return "Successfully uploaded"
    except (Exception, psycopg2.DatabaseError) as error:

        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return error


class Command(BaseCommand):
    help = "Seed database with Indexer API"

    def handle(self, *args, **options):
        self.stdout.write("Seeding accounts command. Started.")
        accounts_upload()
        self.stdout.write("...Completed")
