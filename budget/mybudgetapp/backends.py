# mybudgetapp/backends.py
from django.contrib.auth.backends import ModelBackend
from .models import Customer
from django.contrib.auth.hashers import check_password

class CustomerAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Look up the user by username
            user = Customer.objects.get(username=username)
            if user.check_password(password):  
                return user
        except Customer.DoesNotExist:
            return None
