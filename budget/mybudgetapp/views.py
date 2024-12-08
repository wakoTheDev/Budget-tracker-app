from django.shortcuts import render,redirect
import bcrypt
from django.contrib import messages
from django.contrib import auth
from .models import *
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.views.decorators.http import require_http_methods
import logging
import json
from datetime import datetime, timedelta
from django.http import HttpResponse,JsonResponse
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
        return redirect("/")
    else:
        logger.info("Logout attempt by an anonymous user.")
    return redirect('login')  



def get_content(request, page):
    if page == "home":
        content = render_to_string("home.html")
    elif page == "profile":
        content = render_to_string("profile.html")
    elif page == "account":
        content = render_to_string("accounts.html")
    elif page == "budget":
        content = render_to_string("budget.html")
    elif page == "schedule":
        content = render_to_string("schedule.html")
    elif page == "wallet":
        content = render_to_string("wallet.html")
    else:
        content = render_to_string('home.html')

    return HttpResponse(content)
def back_to_schedule(requst):
    return HttpResponse(render_to_string("schedule.html"))

def get_nav_content(request, page):
    if page == "monthly":
        content = render_to_string("monthly.html")
    elif page == "weekly":
        content = render_to_string("weekly.html")
    elif page == "daily":
        content = render_to_string("daily.html")
    else:
        content = render_to_string("annually.html")
    return HttpResponse(content)


def user_dashboard(request):
    return render(request,'dashboard.html',{})

def limit_form(request):
    return render(request, 'limits.html')

def set_account_limits(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        limit = request.POST.get('limit')
        account_name = request.POST.get('account_name')
        account_number = request.POST.get('account_number')
        
        Limits.objects.create(limit=limit,account_name=account_name,account_number=account_number)
                
        # Return a JSON response
        account_name = request.POST.get('account_name')
        return JsonResponse({'message': 'Limit saved successfully!', 'limit': limit, 'account_name':account_name }, status=200)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def scheduler(request):
    return render(request,'payment_scheduler.html')
@csrf_exempt
def add_payment_schedule(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            schedule = PaymentSchedule.objects.create(
                scheduled_date = data['date'],
                amount = data['amount'],
                recurrence = data.get('recurrence',''),
                description = data.get('description','')
            )
            response_data = {
            'success': True,
            'schedule': {
                'date': data['date'],
                'amount': data['amount'],
                'recurrence': data['recurrence'],
                'description': data['description'],
            }
        }
            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({'success':False,'error':str(e)})

@require_http_methods(["DELETE"])
@csrf_exempt
def delete_schedule(request, schedule_id):
    try:
        schedule = get_object_or_404(PaymentSchedule, id=schedule_id)
        schedule.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["PATCH"])
@csrf_exempt
def update_schedule(request, schedule_id):
    try:
        data = json.loads(request.body)
        schedule = get_object_or_404(PaymentSchedule, id=schedule_id)
        
        if 'date' in data:
            schedule.scheduled_date = data['date']
        if 'recurrence' in data:
            schedule.recurrence = data['recurrence']
        if 'description' in data:
            schedule.description = data['description']
        
        schedule.save()
        return JsonResponse({
            'success': True, 
            'schedule': schedule.to_dict()
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
    
    
def fetch_earnings(request):
    pass



@require_http_methods(["GET"])
def get_schedules(request):
    schedules = PaymentSchedule.objects.all()
    return JsonResponse({
        'schedules': [schedule.to_dict() for schedule in schedules]
    })


@csrf_exempt
@require_http_methods(["POST"])
def get_upcoming_schedules(request):
    try:
        # Parse request body
        body = json.loads(request.body)
        start_date = body.get('start_date', datetime.date.today())
        end_date = body.get('end_date', (datetime.today() + timedelta(days=30)).date())
        
        # Ensure start_date and end_date are datetime objects
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        # Fetch schedules within the next 30 days
        schedules = PaymentSchedule.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).order_by('sceduled_date')

        # Prepare schedule data
        schedule_list = [{
            'id': schedule.id,
            'description': schedule.description,
            'date': schedule.scheduled_date.isoformat()
        } for schedule in schedules]

        return JsonResponse({
            'schedules': schedule_list,
            'count': len(schedule_list)
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def create_revenue_visualization(request):
    pass

def create_annual_schedule(request):
    pass
def create_weekly_schedule(request):
    pass
def create_daily_schedule(request):
    pass
def create_monthly_schedule(request):
    pass

def profile(request):
    pass

def accounts(request):
    pass
