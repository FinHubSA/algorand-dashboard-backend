from django.db import models

class AccountType(models.Model):
    AccountTypeID = models.IntegerField(primary_key=True)
    Type = models.CharField(max_length=100)


class InstrumentType(models.Model):
    InstrumentTypeID = models.IntegerField(primary_key=True)
    Type = models.CharField(max_length=100)


class Account(models.Model):
    Address = models.CharField(max_length=100, blank=False, primary_key=True)
    AccountTypeID = models.ForeignKey(AccountType, on_delete=models.CASCADE)
    Balance = models.DecimalField(max_digits=30, decimal_places=16)
    Name = models.CharField(max_length=200)

class Transaction(models.Model):
    TransactionID = models.CharField(max_length=100, blank=False, primary_key=True)
    Sender = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='Sender')
    Receiver = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='Receiver')
    Amount = models.DecimalField(max_digits=30, decimal_places=16)
    InstrumentTypeID = models.ForeignKey(InstrumentType, on_delete=models.CASCADE)
    Timestamp = models.DateField()
    
