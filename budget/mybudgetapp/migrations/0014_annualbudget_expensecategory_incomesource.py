# Generated by Django 5.1.3 on 2024-12-11 02:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mybudgetapp', '0013_monthlybudget_incomesources_expensecategories'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnnualBudget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('year', models.IntegerField()),
                ('total_monthly_income', models.DecimalField(decimal_places=2, max_digits=12)),
                ('total_monthly_expenses', models.DecimalField(decimal_places=2, max_digits=12)),
                ('monthly_surplus', models.DecimalField(decimal_places=2, max_digits=12)),
                ('annual_surplus', models.DecimalField(decimal_places=2, max_digits=12)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ExpenseCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=100)),
                ('monthly_budget', models.DecimalField(decimal_places=2, max_digits=10)),
                ('budget', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expense_categories', to='mybudgetapp.annualbudget')),
            ],
        ),
        migrations.CreateModel(
            name='IncomeSource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(max_length=200)),
                ('monthly_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('budget', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='income_sources', to='mybudgetapp.annualbudget')),
            ],
        ),
    ]
