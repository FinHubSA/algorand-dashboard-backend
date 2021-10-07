from django.db import models

# Create your models here.


class Account_Type(models.Model):
    Account_TypeID = models.IntegerField(primary_key=True)
    Type = models.CharField(max_length=100)


class Instrument_Type(models.Model):
    Instrument_TypeID = models.IntegerField(primary_key=True)
    Type = models.CharField(max_length=100)


class Account(models.Model):
    Address = models.CharField(max_length=100, blank=False, primary_key=True)
    Account_TypeID = models.ForeignKey(
        Account_Type, on_delete=models.CASCADE)
    Balance = models.IntegerField()
    Name = models.CharField(max_length=200)


class Transaction(models.Model):
    Transaction_ID = models.CharField(
        max_length=100, blank=False, primary_key=True)
    Sender = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name='Sender')
    Receiver = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name='Receiver')
    Instrument_TypeID = models.ForeignKey(
        Instrument_Type, on_delete=models.CASCADE)
    Timestamp = models.DateField()
    Amount = models.IntegerField()
