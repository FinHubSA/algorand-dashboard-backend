# Generated by Django 3.2.8 on 2022-04-08 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_analytics', '0003_transaction_roundtime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='RoundTime',
            field=models.IntegerField(default=0),
        ),
    ]