# Generated by Django 3.2.8 on 2022-04-12 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_analytics', '0004_alter_transaction_roundtime'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='ReceiverTypeId',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='transaction',
            name='SenderTypeId',
            field=models.IntegerField(default=0),
        ),
    ]
