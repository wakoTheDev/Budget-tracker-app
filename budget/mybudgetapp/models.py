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



class Limits(models.Model):
    limit = models.DecimalField(max_digits=10, decimal_places=2)
    account_name = models.CharField(max_length=255, null=False, blank=False)
    account_number = models.CharField(max_length=15, blank=True, null=True)
 


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