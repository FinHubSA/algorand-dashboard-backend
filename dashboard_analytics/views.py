
# Create your views here.
from django.shortcuts import render

from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status

from dashboard_analytics.models import AccountType, InstrumentType, Account, Transaction
from dashboard_analytics.serializers import AccountTypeSerializer, InstrumentTypeSerializer, AccountSerializer, TransactionSerializer
from rest_framework.decorators import api_view


@api_view(['GET', 'POST', 'DELETE'])
def account_list(request):
    accounts = Account.objects.all()

    if request.method == 'GET':
        accounts_serializer = AccountSerializer(accounts, many=True)
        return JsonResponse(accounts_serializer.data, safe=False)
