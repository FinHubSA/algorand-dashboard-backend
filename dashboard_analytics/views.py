
# Create your views here.
from django.shortcuts import render

from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status

from dashboard_analytics.models import Account_Type, Instrument_Type, Account, Transaction
from dashboard_analytics.serializers import Account_TypeSerializer, Instrument_TypeSerializer, AccountSerializer, TransactionSerializer
from rest_framework.decorators import api_view


@api_view(['GET', 'POST', 'DELETE'])
def account_list(request):
    #accounts = Account.objects.get(pk="AdressTesting1234")

    if request.method == 'GET':
        #accounts_serializer = AccountSerializer(accounts, many=True)
        hello = "Welcome to the api Takunda!"
        return JsonResponse(hello, safe=False)
