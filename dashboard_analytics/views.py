
# Create your views here.
from django.shortcuts import render
from django.db.models import Avg, Count, Min, Sum
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http import HttpResponse
from django.core import serializers
from django.db.models import F

from dashboard_analytics.models import AccountType, InstrumentType, Account, Transaction
from dashboard_analytics.serializers import AccountTypeSerializer, InstrumentTypeSerializer, AccountSerializer, TransactionSerializer
from rest_framework.decorators import api_view


@api_view(['GET'])
def account_list(request):
    accounts = Account.objects.all()

    if request.method == 'GET':
        accounts_serializer = AccountSerializer(accounts, many=True)
        return JsonResponse(accounts_serializer.data, safe=False)


@api_view(['POST'])
def node_transactions(request):
    fromDate = request.data.get('from','')
    toDate = request.data.get('to','')
    print("from: "+fromDate+" to: "+toDate)
    transaction_node = Transaction.objects.select_related(
        'Sender__AccountTypeID', 'Receiver__AccountTypeID', "InstrumentTypeID")
    node_data = transaction_node.values(
        id=F("TransactionID"),
        amount=F("Amount"),
        sender=F("Sender"),
        receiver=F("Receiver"),
        sender_balance=F("Sender__Balance"),
        receiver_balance=F("Receiver__Balance"),
        sender_type=F("Sender__AccountTypeID__Type"),
        receiver_type=F("Receiver__AccountTypeID__Type"),
        instrument_type=F("InstrumentTypeID__Type"))
    if request.method == 'POST':
        return JsonResponse(list(node_data), safe=False)


@api_view(['GET'])
def total_transactions(request):
    transactions_total = Transaction.objects.count()
    total_transactions = {
        "total_transactions": transactions_total
    }
    if request.method == 'GET':
        return JsonResponse(total_transactions, safe=False)


@api_view(['GET'])
def total_volume(request):
    total_volume = Account.objects.aggregate(Sum('Balance'))

    volume_total = {
        "total_volume": total_volume["Balance__sum"]
    }
    if request.method == 'GET':
        return JsonResponse(volume_total, safe=False)


@api_view(['GET'])
def most_active_addresses(request):
    most_active_addresses = list(Account.objects.annotate(transaction_count=Count(
        "Sender", distinct=True) + Count("Receiver", distinct=True)).values("Address", "transaction_count"))
    if request.method == 'GET':
        return JsonResponse(most_active_addresses[:6], safe=False)


@api_view(['GET'])
def account_type_total(request):
    type_totals = list(AccountType.objects.annotate(account_type_sum=Sum(
        "account__Balance")).values_list('Type', 'account_type_sum'))
    if request.method == 'GET':
        return JsonResponse(type_totals, safe=False)
