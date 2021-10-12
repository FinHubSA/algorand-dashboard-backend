from rest_framework import serializers
from dashboard_analytics.models import AccountType, InstrumentType, Account, Transaction


class AccountTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccountType
        fields = ('AccountTypeID',
                  'Type',
                  )


class InstrumentTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = InstrumentType
        fields = ('InstrumentTypeID',
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
        fields = ('TransactionID',
                  'Timestamp',
                  'InstrumentTypeID',
                  'Receiver',
                  'Sender'
                  )
