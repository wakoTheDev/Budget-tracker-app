from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid

# Define the custom manager
class CustomerManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)  # Hash the password before saving
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email, password, and superuser rights.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)







class Customer(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=256)
    phone = models.CharField(max_length=15, blank=True, null=True)
    username = models.CharField(max_length=50,unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=True)
    
    
    # Set custom related_name for groups and user_permissions
    groups = models.ManyToManyField(
        'auth.Group', 
        related_name='customer_set',  
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', 
        related_name='customer_set',  
        blank=True
    )
    
    # Link to the custom manager
    objects = CustomerManager()

    USERNAME_FIELD = 'username'  
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name','password']   

    def __str__(self):
        return self.username



class Limit(models.Model):
    account = models.OneToOneField('Account', on_delete=models.CASCADE, related_name='limit')
    max_expenditure = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0.00)],
        verbose_name="Max Expenditure Limit"
    )
    created_at = models.DateTimeField(auto_now_add=True)


class PaymentSchedule(models.Model):
    # Unique identifier for more robust tracking
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )

    # Comprehensive status choices with more granular states
    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        SCHEDULED = 'SCHEDULED', _('Scheduled')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        COMPLETED = 'COMPLETED', _('Completed')
        FAILED = 'FAILED', _('Failed')
        CANCELLED = 'CANCELLED', _('Cancelled')

    # More detailed recurrence options
    class RecurrenceChoices(models.TextChoices):
        ONE_TIME = 'ONE_TIME', _('One-time')
        DAILY = 'DAILY', _('Daily')
        WEEKLY = 'WEEKLY', _('Weekly')
        BI_WEEKLY = 'BI_WEEKLY', _('Bi-Weekly')
        MONTHLY = 'MONTHLY', _('Monthly')
        QUARTERLY = 'QUARTERLY', _('Quarterly')
        SEMI_ANNUALLY = 'SEMI_ANNUALLY', _('Semi-Annually')
        ANNUALLY = 'ANNUALLY', _('Annually')

    # Scheduled date with additional constraints
    scheduled_date = models.DateField(
        verbose_name=_('Scheduled Date'),
        help_text=_('Date when the payment is scheduled to occur'),
        validators=[
            MinValueValidator(
                limit_value=timezone.now().date(), 
                message=_('Scheduled date cannot be in the past')
            )
        ]
    )

    # Amount with more robust validation
    amount = models.DecimalField(
        verbose_name=_('Payment Amount'),
        max_digits=10, 
        decimal_places=2, 
        validators=[
            MinValueValidator(0.01, message=_('Amount must be greater than zero')),
            MaxValueValidator(100000, message=_('Amount exceeds maximum limit'))
        ]
    )

    # Status field with more context
    status = models.CharField(
        verbose_name=_('Payment Status'),
        max_length=20, 
        choices=StatusChoices.choices, 
        default=StatusChoices.PENDING
    )

    # Enhanced description field
    description = models.TextField(
        verbose_name=_('Payment Description'),
        blank=True, 
        null=True,
        max_length=500,
        help_text=_('Optional detailed description of the payment')
    )

    # Recurrence with more options and metadata
    recurrence = models.CharField(
        verbose_name=_('Recurrence Pattern'),
        max_length=20, 
        choices=RecurrenceChoices.choices, 
        default=RecurrenceChoices.ONE_TIME
    )

    # Timestamps with more descriptive names
    created_at = models.DateTimeField(
        verbose_name=_('Creation Timestamp'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name=_('Last Update Timestamp'),
        auto_now=True
    )

    # Optional fields for additional context
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_schedules',
        verbose_name=_('Associated User'),
        null=True,
        blank=True
    )

    category = models.CharField(
        verbose_name=_('Payment Category'),
        max_length=50,
        blank=True,
        null=True,
        help_text=_('Optional categorization of the payment')
    )

    # Method to determine if the schedule is active
    def is_active(self):
        return self.status in [
            self.StatusChoices.PENDING, 
            self.StatusChoices.SCHEDULED, 
            self.StatusChoices.IN_PROGRESS
        ]

    # Custom string representation
    def __str__(self):
        return _("Payment of ${} scheduled for {} ({})").format(self.amount, self.scheduled_date, self.status)

    # Method for serialization 
    def to_dict(self):
        return {
            'id': str(self.id),
            'scheduled_date': self.scheduled_date.strftime('%Y-%m-%d'),
            'amount': str(self.amount),
            'status': self.status,
            'description': self.description or '',
            'recurrence': self.recurrence,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    class Meta:
        verbose_name = _('Payment Schedule')
        verbose_name_plural = _('Payment Schedules')
        ordering = ['-scheduled_date', '-created_at']
        
        # Add database-level constraints
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gt=0), 
                name='positive_amount'
            )
        ]
        

class Account(models.Model):
    ACCOUNT_TYPES = [
        ('phone', 'Phone Number'),
        ('bank', 'Bank Account'),
        ('credit_card', 'Credit Card'),
        ('crypto', 'Crypto Wallet')
    ]
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="accounts")
    account_type = models.CharField(max_length=30, choices=ACCOUNT_TYPES)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    bank_account_number = models.CharField(max_length=20, null=True, blank=True)
    bank_name = models.CharField(max_length=50, null=True, blank=True) 
    credit_card_number = models.CharField(max_length=20, null=True, blank=True)
    wallet_address = models.CharField(max_length=200, null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    cvc = models.IntegerField(null=True, blank=True)
    account_name=models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.account_name} ({self.account_type}) - {self.customer.username}"

    class Meta:
        unique_together = ('customer', 'account_name')
        

class WeeklyBudget(models.Model):
    # User who created the budget
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='weekly_budgets')
    
    # Income Details
    primary_income = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    additional_income = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_income = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Expense Allocations 
    housing_expense = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    utilities_expense = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    groceries_expense = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    transportation_expense = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    entertainment_expense = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    savings_expense = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Total Expense Calculation
    total_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Financial Goals
    emergency_fund_target = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    specific_goal_description = models.CharField(max_length=255, null=True, blank=True)
    goal_progress_notes = models.TextField(null=True, blank=True)
    
    # Net Surplus/Deficit
    net_surplus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Tracking and Metadata
    created_at = models.DateTimeField(default=timezone.now)
    week_start_date = models.DateField()
    
    def save(self, *args, **kwargs):
        # Calculate total income
        self.total_income = self.primary_income + self.additional_income
        
        # Calculate total expense based on percentages
        expense_categories = [
            self.housing_expense, 
            self.utilities_expense, 
            self.groceries_expense, 
            self.transportation_expense, 
            self.entertainment_expense, 
            self.savings_expense
        ]
        
        total_percentage = sum(expense_categories)
        
        if total_percentage > 100:
            raise ValueError("Total expense percentage cannot exceed 100%")
        
        self.total_expense = self.total_income * (total_percentage / 100)
        
        # Calculate net surplus
        self.net_surplus = self.total_income - self.total_expense
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Weekly Budget for {self.user.username} - Week of {self.week_start_date}"
    
    class Meta:
        verbose_name = "Weekly Budget"
        verbose_name_plural = "Weekly Budgets"
        ordering = ['-created_at']
        
class DailyBudget(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    
    # Morning Financial Check-In
    daily_budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    financial_goal = models.CharField(max_length=255, blank=True, null=True)
    expense_tracking_method = models.CharField(max_length=50, blank=True, null=True)
    
    # Expense Management
    essential_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discretionary_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    savings_allocation_percentage = models.IntegerField(default=0)
    expense_notes = models.TextField(blank=True, null=True)
    
    # Evening Reconciliation
    total_daily_spending = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_saved = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tomorrow_budget_plan = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    goal_achieved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Daily Budget - {self.user.username} - {self.date}"
    
    
    
class MonthlyBudget(models.Model):
    PERIOD_CHOICES = [
        ('monthly', 'Monthly'),
        ('weekly', 'Weekly'),
        ('daily', 'Daily')
    ]

    MONTH_CHOICES = [
        ('1', 'January'),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August'),
        ('9', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December')
    ]

    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    month = models.CharField(max_length=2, choices=MONTH_CHOICES)
    year = models.IntegerField()
    period_type = models.CharField(max_length=10, choices=PERIOD_CHOICES, default='monthly')
    
    total_income = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    budget_surplus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    financial_goal = models.CharField(max_length=255, blank=True, null=True)
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    additional_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_month_display()} {self.year} Budget"

class IncomeSources(models.Model):
    monthly_budget = models.ForeignKey(MonthlyBudget, related_name='income_sources', on_delete=models.CASCADE)
    source = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.source}: ${self.amount}"

class ExpenseCategories(models.Model):
    monthly_budget = models.ForeignKey(MonthlyBudget, related_name='expense_categories', on_delete=models.CASCADE)
    category = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.category}: ${self.amount}"
    
class AnnualBudget(models.Model):
    name = models.CharField(max_length=200)
    year = models.IntegerField()
    total_monthly_income = models.DecimalField(max_digits=12, decimal_places=2)
    total_monthly_expenses = models.DecimalField(max_digits=12, decimal_places=2)
    monthly_surplus = models.DecimalField(max_digits=12, decimal_places=2)
    annual_surplus = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.year} Budget"

class IncomeSource(models.Model):
    budget = models.ForeignKey(AnnualBudget, related_name='income_sources', on_delete=models.CASCADE)
    source = models.CharField(max_length=200)
    monthly_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.source} - ${self.monthly_amount}"

class ExpenseCategory(models.Model):
    budget = models.ForeignKey(AnnualBudget, related_name='expense_categories', on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    monthly_budget = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.category} - ${self.monthly_budget}"