from rest_framework import serializers
from dashboard_analytics.models import Account_Type, Instrument_Type, Account, Transaction


class Account_TypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account_Type
        fields = ('Account_TypeID',
                  'Type',
                  )


class Instrument_TypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Instrument_Type
        fields = ('Instrument_TypeID',
                  'Type',
                  )


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ('Address',
                  'Balance',
                  'Name',
                  )


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = ('Transaction_ID',
                  'Timestamp',
                  'Instrument_TypeID',
                  'Receiver',
                  'Sender'
                  )
