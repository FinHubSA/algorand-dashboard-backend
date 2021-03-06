
# Create your views here.
from django.shortcuts import render
from django.db.models import Avg, Count, Min, Sum
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.response import Response
from django.core import serializers
from django.db.models import F, Func, Value, CharField

import copy

from dashboard_analytics.models import AccountType, InstrumentType, Account, Transaction
from dashboard_analytics.serializers import AccountTypeSerializer, InstrumentTypeSerializer, AccountSerializer, TransactionSerializer
from rest_framework.decorators import api_view

@api_view(['GET'])
def account_list(request):
    accounts = Account.objects.all()

    if request.method == 'GET':
        accounts_serializer = AccountSerializer(accounts, many=True)
        return Response(accounts_serializer.data)

@api_view(['POST'])
def most_active_accounts(request):
    fromDate = request.data.get('from','')#,'2020-11-03')
    toDate = request.data.get('to','')#'2021-11-03')

    results = {}

    transaction_nodes = Transaction.objects.filter(Timestamp__range=[fromDate, toDate]).select_related("Sender__AccountTypeID", "Receiver__AccountTypeID")
    sender_data = transaction_nodes.values(
        account=F("Sender")).annotate(account_type=F("Sender__AccountTypeID__Type"), payments=Sum("Amount"), balance=F("Sender__Balance"), number_of_payments=Count("TransactionID"))
    
    receiver_data = transaction_nodes.values(
        account=F("Receiver")).annotate(account_type=F("Receiver__AccountTypeID__Type"), receipts=Sum("Amount"), balance=F("Receiver__Balance"), number_of_receipts=Count("TransactionID"))
    
    for s_item in sender_data.iterator():
        item = copy.deepcopy(s_item)

        item["receipts"] = 0
        item["number_of_receipts"] = 0

        item["number_of_transactions"] = item["number_of_payments"]
        item["net_transactions_value"] = -1 * round(item["payments"], 2)
        item["abs_transactions_value"] = round(item["payments"], 2)
        results[item["account"]] = item

    for r_item in receiver_data.iterator():
        item = copy.deepcopy(r_item)
        if item["account"] in results.keys():
            # results has sender fields: payments and num_of_payments
            # item only has receiver fields: receipts and num_of_receipts
            result = results[item["account"]]
            # put sender fields into item
            item["payments"] = result["payments"]
            item["number_of_payments"] = result["number_of_payments"]
            # format receipts field
            item["receipts"] = item["receipts"]

            item["number_of_transactions"] = item["number_of_receipts"] + result["number_of_payments"]
            item["net_transactions_value"] = item["receipts"] - result["payments"]
            item["abs_transactions_value"] = item["receipts"] + result["payments"]
            results[item["account"]] = item
        else:
            item["payments"] = 0
            item["number_of_payments"] = 0
            # format receipts field
            item["receipts"] = item["receipts"]

            item["number_of_transactions"] = item["number_of_receipts"]
            item["net_transactions_value"] = item["receipts"]
            item["abs_transactions_value"] = item["receipts"]
            results[item["account"]] = item
    
    if request.method == "POST":
        return Response(results)

@api_view(['POST'])
def node_transactions(request):
    fromDate = request.data.get('from','')
    toDate = request.data.get('to','')
    print("from: "+fromDate+" to: "+toDate)
    transaction_node = Transaction.objects.filter(Timestamp__range=[fromDate, toDate]).select_related('Sender__AccountTypeID', 'Receiver__AccountTypeID', "InstrumentTypeID")
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
        return Response(list(node_data))


@api_view(['POST'])
def total_transactions(request):
    fromDate = request.data.get('from','')
    toDate = request.data.get('to','')

    transactions_total = Transaction.objects.filter(Timestamp__range=[fromDate, toDate]).count()
    total_transactions = {
        "total_transactions": transactions_total
    }
    if request.method == 'POST':
        return Response(total_transactions)

@api_view(['POST'])
def average_transaction_amount(request):
    fromDate = request.data.get('from','')
    toDate = request.data.get('to','')

    transaction_node = Transaction.objects.filter(Timestamp__range=[fromDate, toDate])
    data = transaction_node.aggregate(average_transaction_amount=Avg("Amount"))
    if request.method == "POST":
        return Response(data)

@api_view(['POST'])
def average_loan_amount(request):
    fromDate = request.data.get('from','')
    toDate = request.data.get('to','')

    transaction_node = Transaction.objects.filter(Timestamp__range=[fromDate, toDate],InstrumentTypeID__Type="Loans and Bonds")
    data = transaction_node.aggregate(average_loan_amount=Avg("Amount"))
    if request.method == "POST":
        return Response(data)

@api_view(['GET'])
def total_volume(request):
    
    total_volume = Account.objects.aggregate(Sum('Balance'))

    volume_total = {
        "total_volume": total_volume["Balance__sum"]
    }

    if request.method == 'GET':
        return Response(volume_total)


@api_view(['GET'])
def most_active_addresses(request):
    most_active_addresses = list(Account.objects.annotate(transaction_count=Count(
        "Sender", distinct=True) + Count("Receiver", distinct=True)).order_by("-transaction_count").values("Address", "transaction_count"))
    if request.method == 'GET':
        return Response(most_active_addresses[:6])


@api_view(['POST'])
def account_type_payments_receipts(request):
    fromDate = request.data.get('from','')
    toDate = request.data.get('to','')

    # select_related obtains all data at one time through multi-table join Association query.
    # It improves performance by reducing the number of database queries.
    # Sender__AccountTypeID is a string of joins. First to Account through Sender FK, 
    #   then to the AccountType through AccountTypeID FK.
    # annotate is the GROUP BY equivalent. In this case it groups by the 
    transaction_node = Transaction.objects.filter(Timestamp__range=[fromDate, toDate]).select_related("Sender__AccountTypeID", "Receiver__AccountTypeID", "InstrumentTypeID")
    node_data = transaction_node.values(
            sender_type=F("Sender__AccountTypeID__Type"),
            receiver_type=F("Receiver__AccountTypeID__Type"), 
            instrument_type=F( "InstrumentTypeID__Type")).annotate(value=Sum("Amount"),payments=Value("true", output_field=CharField()))
    if request.method == "POST":
        return Response(list(node_data))
    
@api_view(['POST'])
def account_type_transaction_volume(request):
    fromDate = request.data.get('from','2020-11-03')
    toDate = request.data.get('to','2021-11-03')
    interval = request.data.get('interval','day')

    date_format = "yyyy-MM-dd"
    if (interval == "month"):
        date_format = "yyyy-MM"
    elif (interval == "year"):
        date_format = "yyyy"
    
    results = {}
    final_results = []

    transaction_nodes = Transaction.objects.filter(
        Timestamp__range=[fromDate, toDate]
    ).select_related(
        "Sender__AccountTypeID", "Receiver__AccountTypeID"
    )
    
    sender_data = transaction_nodes.values(
        account_type=F("Sender__AccountTypeID__Type"),
        formatted_date=Func(
            F('Timestamp'),
            Value(date_format),
            function='to_char',
            output_field=CharField()
        )).annotate(
            amount=Sum("Amount"),
            count=Count("TransactionID")).order_by("formatted_date")

    receiver_data = transaction_nodes.values(
        account_type=F("Receiver__AccountTypeID__Type"),
        formatted_date=Func(
            F('Timestamp'),
            Value(date_format),
            function='to_char',
            output_field=CharField()
        )).annotate(
            amount=Sum("Amount"),
            count=Count("TransactionID")).order_by("formatted_date")
    
    dates = set()

    for item in sender_data.iterator():
        formatted_date = item["formatted_date"]
        dates.add(formatted_date)

        if item["account_type"] in results.keys():
            results[item["account_type"]][formatted_date] = item["amount"]
        else:
            results[item["account_type"]] = {}
            results[item["account_type"]][formatted_date] = item["amount"]

    for item in receiver_data.iterator():
        formatted_date = item["formatted_date"]
        dates.add(formatted_date)

        if item["account_type"] in results.keys():
            if formatted_date in results[item["account_type"]]:
                value = results[item["account_type"]][formatted_date]
                results[item["account_type"]][formatted_date] = value + item["amount"]
            else:
                results[item["account_type"]][formatted_date] = item["amount"]
        else:
            results[item["account_type"]] = {}
            results[item["account_type"]][formatted_date] = item["amount"]

    # Put an array in final results
    for account_type, date_values in results.items():
        # fill up empty dates
        for date in dates:
            if not (date in date_values.keys()):
                final_results.append({"account_type":account_type,"date":date,"value":"0"})

        for date, value in date_values.items():
            final_results.append({"account_type":account_type,"date":date,"value":value})

    sorted_final_results = sorted(final_results, key=lambda k: (k["account_type"].lower(), k["date"])) 

    if request.method == "POST":
        return Response(sorted_final_results)
    
@api_view(['GET'])
def account_type_total(request):
    account_node = Account.objects.select_related("AccountTypeID")
    node_data = account_node.values(
            account_type=F("AccountTypeID__Type"
        )).annotate(value=Sum("Balance"))
    if request.method == 'GET':
        return Response(list(node_data))
