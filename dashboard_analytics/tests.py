import json
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from dashboard_analytics.models import AccountType, InstrumentType, Account, Transaction
from .serializers import AccountTypeSerializer, InstrumentTypeSerializer, AccountSerializer, TransactionSerializer

client = Client()

class AccountTestCase(TestCase):
    def setUp(self):
        AccountType.objects.create(AccountTypeID=0,Type="Unknown")
        AccountType.objects.create(AccountTypeID=1,Type="Household")
        AccountType.objects.create(AccountTypeID=2,Type="Firm")
        AccountType.objects.create(AccountTypeID=3,Type="Bank")
        AccountType.objects.create(AccountTypeID=4,Type="LSP")
        AccountType.objects.create(AccountTypeID=5,Type="CentralBank")
        
        InstrumentType.objects.create(InstrumentTypeID=1,Type="Bank Notes")
        InstrumentType.objects.create(InstrumentTypeID=2,Type="Deposits")
        InstrumentType.objects.create(InstrumentTypeID=3,Type="Loans and Bonds")
        InstrumentType.objects.create(InstrumentTypeID=4,Type="Reserves")
        InstrumentType.objects.create(InstrumentTypeID=5,Type="CBDC")
        InstrumentType.objects.create(InstrumentTypeID=6,Type="Open Market Operations")

        Account.objects.create(Address="HOUSEHOLD1", AccountTypeID_id=1, Balance=10, Name="")
        Account.objects.create(Address="HOUSEHOLD2", AccountTypeID_id=1, Balance=10, Name="")
        Account.objects.create(Address="FIRM1", AccountTypeID_id=2, Balance=10, Name="")
        Account.objects.create(Address="BANK1", AccountTypeID_id=3, Balance=10, Name="")
        Account.objects.create(Address="LSP1", AccountTypeID_id=4, Balance=10, Name="")
        Account.objects.create(Address="CENTRALBANK", AccountTypeID_id=5, Balance=10, Name="")

        Transaction.objects.create(TransactionID=1,Sender_id="HOUSEHOLD1",Receiver_id="BANK1",Amount=5,InstrumentTypeID_id=2,Timestamp="2021-02-02")
        Transaction.objects.create(TransactionID=2,Sender_id="HOUSEHOLD2",Receiver_id="BANK1",Amount=5,InstrumentTypeID_id=2,Timestamp="2021-02-02")
        Transaction.objects.create(TransactionID=3,Sender_id="BANK1",Receiver_id="HOUSEHOLD1",Amount=5,InstrumentTypeID_id=3,Timestamp="2021-02-02")
        Transaction.objects.create(TransactionID=4,Sender_id="BANK1",Receiver_id="HOUSEHOLD2",Amount=5,InstrumentTypeID_id=3,Timestamp="2021-02-02")
        Transaction.objects.create(TransactionID=5,Sender_id="HOUSEHOLD1",Receiver_id="FIRM1",Amount=2,InstrumentTypeID_id=1,Timestamp="2021-02-02")
        Transaction.objects.create(TransactionID=6,Sender_id="HOUSEHOLD2",Receiver_id="FIRM1",Amount=2,InstrumentTypeID_id=1,Timestamp="2021-02-02")
        Transaction.objects.create(TransactionID=7,Sender_id="BANK1",Receiver_id="CENTRALBANK",Amount=10,InstrumentTypeID_id=4,Timestamp="2021-02-02")
        Transaction.objects.create(TransactionID=8,Sender_id="BANK1",Receiver_id="FIRM1",Amount=10,InstrumentTypeID_id=3,Timestamp="2021-02-02")
        Transaction.objects.create(TransactionID=9,Sender_id="HOUSEHOLD1",Receiver_id="HOUSEHOLD2",Amount=3,InstrumentTypeID_id=1,Timestamp="2021-02-02")


    def test_account_list(self):
        response = client.get(reverse('account_list'))
        accounts = Account.objects.all()
        serializer = AccountSerializer(accounts, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_total_transactions(self):
        self.valid_payload = {'from': '','to': ''}
        response = client.post(reverse('total_transactions', content_type='application/json'))
        self.assertEqual(response.data, {"total_transactions": 9})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_total_volume(self):
        response = client.get(reverse('total_volume'))
        self.assertEqual(response.data, {"total_volume": 60})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_most_active_addresses(self):
        response = client.get(reverse('most_active_addresses'))
        self.assertEqual(response.data[0], {"Address": "BANK1","transaction_count":6})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
