from django.core.management.base import BaseCommand, CommandError
import requests
from dashboard_analytics.models import AccountType, InstrumentType, Account, Transaction

# file to indexer API and save into postgres database
# Indexer port configuration
INDEXER_PORT = "123"
# bla bla bla


def get_data():
    print("Begin grabbing data from indexer API")
    # code below


def seed_data():
    print("Begin seeding data into database")
    # code below


class Command(BaseCommand):
    help = "Seed database with Indexer API"

    def handle(self, *args, **options):
        self.stdout.write("My sample command just ran.")  # NEW
        # seed_data()
        self.stdout.write("completed")
