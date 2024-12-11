# Generated by Django 5.1.3 on 2024-12-11 01:00

import datetime
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mybudgetapp', '0011_weeklybudget'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentschedule',
            name='scheduled_date',
            field=models.DateField(help_text='Date when the payment is scheduled to occur', validators=[django.core.validators.MinValueValidator(limit_value=datetime.date(2024, 12, 11), message='Scheduled date cannot be in the past')], verbose_name='Scheduled Date'),
        ),
        migrations.CreateModel(
            name='DailyBudget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('daily_budget', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('financial_goal', models.CharField(blank=True, max_length=255, null=True)),
                ('expense_tracking_method', models.CharField(blank=True, max_length=50, null=True)),
                ('essential_expenses', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('discretionary_expenses', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('savings_allocation_percentage', models.IntegerField(default=0)),
                ('expense_notes', models.TextField(blank=True, null=True)),
                ('total_daily_spending', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('amount_saved', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('tomorrow_budget_plan', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('goal_achieved', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
