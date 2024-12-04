from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

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




# from django.contrib.auth.models import User
# from datetime import timedelta

# class ScheduledExpenditure(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     title = models.CharField(max_length=100)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     recipient = models.CharField(max_length=100)
#     category = models.CharField(max_length=50, choices=[
#         ('Rent', 'Rent'),
#         ('Utilities', 'Utilities'),
#         ('Subscriptions', 'Subscriptions'),
#         ('Groceries', 'Groceries'),
#         ('Other', 'Other')
#     ])
#     frequency = models.CharField(max_length=50, choices=[
#         ('Daily', 'Daily'),
#         ('Weekly', 'Weekly'),
#         ('Monthly', 'Monthly'),
#         ('Yearly', 'Yearly')
#     ])
#     next_payment_date = models.DateField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     def is_due(self):
#         return self.next_payment_date <= timezone.now().date()

#     def update_next_payment(self):
#         if self.frequency == 'Daily':
#             self.next_payment_date += timedelta(days=1)
#         elif self.frequency == 'Weekly':
#             self.next_payment_date += timedelta(weeks=1)
#         elif self.frequency == 'Monthly':
#             self.next_payment_date += timedelta(days=30)  # Approximate
#         elif self.frequency == 'Yearly':
#             self.next_payment_date += timedelta(days=365)
#         self.save()

# class AutomatedPayment(models.Model):
#     scheduled_expenditure = models.ForeignKey(ScheduledExpenditure, on_delete=models.CASCADE)
#     status = models.CharField(max_length=50, choices=[
#         ('Pending', 'Pending'),
#         ('Authorized', 'Authorized'),
#         ('Executed', 'Executed'),
#         ('Declined', 'Declined')
#     ], default='Pending')
#     executed_at = models.DateTimeField(null=True, blank=True)

