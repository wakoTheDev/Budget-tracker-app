# Generated by Django 5.1.3 on 2024-12-10 11:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mybudgetapp', '0009_account_bank_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='password',
        ),
    ]
