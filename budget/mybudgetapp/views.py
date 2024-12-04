from django.shortcuts import render,redirect
import bcrypt
from django.contrib import messages
from django.contrib import auth
from .models import *
import logging
from django.http import HttpResponse
from django.template.loader import render_to_string

logger = logging.getLogger('my_custom_logger')

# Create your views here.
def home(request):
    return render(request,'register.html',{})


def register(request):
    if request.method == "POST":
        first_name = request.POST['firstName']
        last_name = request.POST['lastName']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirmPassword']
        phone = request.POST['phone']
        username = request.POST['username']
        
        # check if the values are null
        if first_name and last_name and first_name and email and password and confirm_password and phone and username:
            # check for password validation and encrypt
            if confirm_password == password:
                #confirming if username is unique
                if Customer.objects.filter(username=username).exists():
                    messages.info(request,"username already taken")
                    return redirect('register')
                try:
                    user = Customer.objects.create_user(first_name=first_name,last_name=last_name,email=email,password=password,phone=phone,username=username)
                    messages.info(request,"Registered successfully")
                    return redirect('login') 
                except Exception as e:
                    messages.error(request, f"Registration failed: {str(e)}")
                    return redirect('register')
            else:
                messages.info(request,"password doesn't match")
                return redirect('register')    
    else:
        return render(request,'register.html')
    
def login(request):
    if request.method == 'POST':
        password = request.POST['password']
        username = request.POST['username']
        # alert if the password is not provided 
        logger.debug('hello function starts')
        if not username or not password:
            logger.debug("Username or password missing.")
            messages.error(request, "Username and password are required.")
            return redirect('login')
        
        user = auth.authenticate(request, username=username, password=password)
        # Authenticate the user
        if user is not None:
            logger.info(f"User authenticated: {user.username}")
            auth.login(request, user)
            return redirect('dashboard')
        else:
            logger.warning("Authentication failed for user: %s", username)
            messages.error(request, "Invalid credentials.")
            return redirect('login')
    else:
        logger.debug("Rendering login page.")
        return render(request, 'login.html')
    
    
def logout(request):
    if request.user.is_authenticated:
        logger.info(f"Logging out user: {request.user.username}")
        auth.logout(request)
        messages.info(request, "logged out successfully.")
    else:
        logger.info("Logout attempt by an anonymous user.")
    return redirect('login')  



def get_content(request, page):
    if page == "home":
        content = render_to_string("home.html")
    elif page == "profile":
        content = render_to_string("profile.html")
    elif page == "account":
        content = render_to_string("account.html")
    elif page == "budget":
        content = render_to_string("budget.html")
    elif page == "schedule":
        content = render_to_string("schedule.html")
    elif page == "wallet":
        content = render_to_string("wallet.html")
    else:
        content = render_to_string('home.html')

    return HttpResponse(content)


def user_dashboard(request):
    return render(request,'dashboard.html',{})

def add_transaction(request):
    pass

# from django.shortcuts import render, redirect
# from django.utils.timezone import now
# from .models import ScheduledExpenditure, AutomatedPayment

# def dashboard(request):
#     scheduled_payments = ScheduledExpenditure.objects.filter(user=request.user)
#     return render(request, 'dashboard.html', {'scheduled_payments': scheduled_payments})

# def add_scheduled_payment(request):
#     if request.method == 'POST':
#         ScheduledExpenditure.objects.create(
#             user=request.user,
#             title=request.POST['title'],
#             amount=request.POST['amount'],
#             recipient=request.POST['recipient'],
#             category=request.POST['category'],
#             frequency=request.POST['frequency'],
#             next_payment_date=request.POST['next_payment_date']
#         )
#         return redirect('dashboard')
#     return render(request, 'add_scheduled_payment.html')

# def authorize_payment(request, payment_id):
#     payment = ScheduledExpenditure.objects.get(id=payment_id, user=request.user)
#     AutomatedPayment.objects.create(
#         scheduled_expenditure=payment,
#         status='Authorized',
#         executed_at=now()
#     )
#     payment.update_next_payment()
#     return redirect('dashboard')

# def decline_payment(request, payment_id):
#     payment = ScheduledExpenditure.objects.get(id=payment_id, user=request.user)
#     AutomatedPayment.objects.create(
#         scheduled_expenditure=payment,
#         status='Declined',
#     )
#     return redirect('dashboard')

