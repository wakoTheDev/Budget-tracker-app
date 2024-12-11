from django.shortcuts import render,redirect
import bcrypt
from django.contrib import messages
from django.contrib import auth
from .models import *
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import make_password
from django.db import transaction
import logging
import json
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.http import HttpResponse,JsonResponse
from django.template.loader import render_to_string

logger = logging.getLogger('my_custom_logger')

# Create your views here.
def home(request):
    return render(request,'landing.html',{})


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
            if user.is_staff:
                return redirect('/admin')
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
        
        Limit.objects.create(limit=limit,account_name=account_name,account_number=account_number)
                
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
    
    
@csrf_exempt
@login_required
def create_account(request):
    if request.method == 'POST':
        # Get the customer object 
        customer = request.user 
        full_name = request.POST['full_name']
        email = request.POST['email']
        account_type = request.POST['account_type'] 
        phone_number = request.POST.get('phone_number')
        bank_account_number = request.POST.get('bank_account') 
        credit_card_number = request.POST.get('credit_card_number')
        wallet_address = request.POST.get('crypto_wallet_address')
        expiry_date = request.POST.get('credit_card_expiry')
        cvc = request.POST.get('credit_card_cvc')
        account_name = request.POST['account_name']
        
        # Check if passwords match
        if full_name:                      
            # Check for existing accounts with the same details
            
            if account_type == 'phone' and Account.objects.filter(phone_number=phone_number).exists():
                return JsonResponse({'status': 'error', 'message': 'An account with this phone number already exists.'})
            elif account_type == 'bank' and Account.objects.filter(bank_account_number=bank_account_number).exists():
                return JsonResponse({'status': 'error', 'message': 'An account with this bank account number already exists.'})
            elif account_type == 'credit_card' and Account.objects.filter(credit_card_number=credit_card_number).exists():
                return JsonResponse({'status': 'error', 'message': 'An account with this credit card number already exists.'})
            elif account_type == 'crypto_wallet' and Account.objects.filter(wallet_address=wallet_address).exists():
                return JsonResponse({'status': 'error', 'message': 'An account with this wallet address already exists.'})
            else:
                # Create new account if no conflicts
                account = Account.objects.create(
                    full_name=full_name,
                    email=email,
                    customer=customer,
                    account_type=account_type,
                    phone_number=phone_number,
                    bank_account_number=bank_account_number,
                    credit_card_number=credit_card_number,
                    wallet_address=wallet_address,
                    expiry_date=expiry_date,
                    cvc=cvc,
                    account_name=account_name
                )
                account.save()
                return JsonResponse({'status': 'success', 'message': 'Account created successfully.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Cannot save empty fields'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
            


def get_accounts(request):
    # Fetch accounts for the logged-in user
    accounts = Account.objects.filter(customer=request.user)
    
    # Prepare accounts data with correct details
    accounts_data = []
    for account in accounts:
        # Initialize data dictionary based on account type
        data = {
            'title': '',
            'details': ''
        }
        
        # Set title and details based on account type
        if account.account_type == 'phone':
            data['title'] = 'Mobile Money'
            data['details'] = f'Registered Phone: {account.phone_number}'
        elif account.account_type == 'bank':
            data['title'] = 'Bank Account'
            data['details'] = f'Account number: {account.bank_account_number}'
        elif account.account_type == 'credit_card':
            data['title'] = 'Credit Card'
            data['details'] = f'Card Number: {account.credit_card_number}'
        elif account.account_type == 'crypto_wallet':
            data['title'] = 'Crypto Wallet'
            data['details'] = f'Wallet address: {account.wallet_address}'
        
        # Add complete account information to the list
        accounts_data.append({
            'id': account.id,
            'account_type': account.account_type,
            'account_name': account.account_name,
            'phone_number': account.phone_number if account.account_type == 'phone' else None,
            'bank_name': account.bank_name if account.account_type == 'bank' else None,
            'bank_account': account.bank_account_number if account.account_type == 'bank' else None,
            'credit_card_number': account.credit_card_number if account.account_type == 'credit_card' else None,
            'credit_card_expiry': account.credit_card_expiry if account.account_type == 'credit_card' else None,
            'crypto_wallet_address': account.wallet_address if account.account_type == 'crypto_wallet' else None,
            'details': data
        })

    # Return the account data as JSON response
    return JsonResponse({'accounts': accounts_data, 'status': 'success'})


@csrf_exempt
def delete_account(request):
    if request.method == 'POST':
        account_id = request.POST.get('account_id')
        if account_id:
                try:
                    # Retrieve and delete the account 
                    account = Account.objects.get(id=account_id)
                    account.delete()
                    return JsonResponse({'status': 'success', 'message': 'Account deleted successfully'})
                except Account.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'Account not found'}, status=404)
        else:
            return JsonResponse({'status': 'error', 'message': 'Account ID is required'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


def create_revenue_visualization(request):
    pass

def create_annual_schedule(request):
    pass

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_weekly_budget(request):
    try:
        # Parse JSON data from request
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['primary_income', 'total_income', 'total_expense', 'net_surplus']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'status': 'error', 
                    'message': f'Missing required field: {field}'
                }, status=400)
        
        # Type checking and conversion
        try:
            primary_income = float(data.get('primary_income', 0))
            total_income = float(data.get('total_income', 0))
            total_expense = float(data.get('total_expense', 0))
            net_surplus = float(data.get('net_surplus', 0))
        except ValueError:
            return JsonResponse({
                'status': 'error', 
                'message': 'Invalid numeric values provided'
            }, status=400)
        
        # Create weekly budget instance
        weekly_budget = WeeklyBudget.objects.create(
            user=request.user,
            primary_income=primary_income,
            additional_income=float(data.get('additional_income', 0)),
            total_income=total_income,
            housing_expense=float(data.get('housing_expense', 0)),
            utilities_expense=float(data.get('utilities_expense', 0)),
            groceries_expense=float(data.get('groceries_expense', 0)),
            transportation_expense=float(data.get('transportation_expense', 0)),
            entertainment_expense=float(data.get('entertainment_expense', 0)),
            savings_expense=float(data.get('savings_expense', 0)),
            total_expense=total_expense,
            net_surplus=net_surplus,
            week_start_date=timezone.now().date()
        )
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Weekly budget created successfully',
            'budget_id': weekly_budget.id
        }, status=201)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON format'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
        
@login_required
@require_http_methods(["POST"])
@csrf_exempt
def create_daily_budget(request):
    try:
        # Parse JSON data from request
        data = json.loads(request.body)
        
        # Create daily budget instance
        daily_budget = DailyBudget.objects.create(
            user=request.user,
            daily_budget=data.get('dailyBudget', 0),
            financial_goal=data.get('financialGoal', ''),
            expense_tracking_method=data.get('expenseTrackingMethod', ''),
            essential_expenses=data.get('essentialExpenses', 0),
            discretionary_expenses=data.get('discretionaryExpenses', 0),
            savings_allocation_percentage=data.get('savingsAllocation', 0),
            expense_notes=data.get('expenseNotes', ''),
            total_daily_spending=data.get('totalDailySpending', 0),
            amount_saved=data.get('amountSaved', 0),
            tomorrow_budget_plan=data.get('tomorrowBudgetPlan', 0),
            goal_achieved=data.get('goalAchieved', False)
        )
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Daily budget created successfully',
            'budget_id': daily_budget.id
        }, status=201)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@csrf_protect
@require_http_methods(["POST"])
def create_monthly_budget(request):
    try:
        # Parse incoming JSON data
        data = json.loads(request.body)
        
        # Start a database transaction
        with transaction.atomic():
            # Create Monthly Budget Entry
            monthly_budget = MonthlyBudget.objects.create(
                user=request.user,  
                month=data.get('month'),
                year=data.get('year'),
                period_type=data.get('period_type'),
                total_income=data.get('total_income'),
                total_expenses=data.get('total_expenses'),
                budget_surplus=data.get('budget_surplus'),
                financial_goal=data.get('financial_goal'),
                goal_amount=data.get('goal_amount'),
                additional_notes=data.get('additional_notes')
            )
            
            # Add Income Sources
            for income_source in data.get('income_sources', []):
                IncomeSources.objects.create(
                    monthly_budget=monthly_budget,
                    source=income_source.get('source'),
                    amount=income_source.get('amount')
                )
            
            # Add Expense Categories
            for expense_category in data.get('expense_categories', []):
                ExpenseCategories.objects.create(
                    monthly_budget=monthly_budget,
                    category=expense_category.get('category'),
                    amount=expense_category.get('amount')
                )
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Monthly budget saved successfully',
            'budget_id': monthly_budget.id
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': str(e)
        }, status=400)



@csrf_protect
@require_http_methods(["POST"])
def save_annual_budget(request):
    try:
        # Parse incoming JSON data
        data = json.loads(request.body)
        
        # Create Annual Budget
        annual_budget = AnnualBudget.objects.create(
            name=data.get('name'),
            year=data.get('year'),
            total_monthly_income=data.get('total_monthly_income'),
            total_monthly_expenses=data.get('total_monthly_expenses'),
            monthly_surplus=data.get('monthly_surplus'),
            annual_surplus=data.get('annual_surplus'),
            notes=data.get('notes', '')
        )

        # Save Income Sources
        income_sources = data.get('income_sources', [])
        for source in income_sources:
            IncomeSource.objects.create(
                budget=annual_budget,
                source=source['source'],
                monthly_amount=source['amount']
            )

        # Save Expense Categories
        expense_categories = data.get('expense_categories', [])
        for expense in expense_categories:
            ExpenseCategory.objects.create(
                budget=annual_budget,
                category=expense['category'],
                monthly_budget=expense['amount']
            )

        return JsonResponse({
            'message': 'Budget saved successfully!', 
            'budget_id': annual_budget.id
        }, status=201)

    except Exception as e:
        return JsonResponse({
            'message': f'Error saving budget: {str(e)}'
        }, status=400)


@require_http_methods(["GET"])
def get_earnings_data(request):
    try:
        # Get the most recent annual budget
        latest_budget = AnnualBudget.objects.latest('created_at')
        
        # Calculate monthly and annual earnings
        monthly_earnings = latest_budget.total_monthly_income
        annual_earnings = monthly_earnings * 12

        return JsonResponse({
            'monthly_earnings': float(monthly_earnings),
            'annual_earnings': float(annual_earnings)
        })
    except AnnualBudget.DoesNotExist:
        return JsonResponse({
            'monthly_earnings': 0,
            'annual_earnings': 0
        })

@require_http_methods(["GET"])
def get_income_sources(request):
    # Get the most recent annual budget
    latest_budget = AnnualBudget.objects.latest('created_at')
    
    # Fetch income sources for the latest budget
    income_sources = IncomeSource.objects.filter(budget=latest_budget).values(
        'source', 
        'monthly_amount'
    )

    return JsonResponse({
        'income_sources': list(income_sources)
    })
    
@require_http_methods(["GET"])
def get_expense_categories(request):
    # Get the most recent annual budget
    latest_budget = AnnualBudget.objects.latest('created_at')
    
    # Fetch expense categories for the latest budget
    expense_categories = ExpenseCategory.objects.filter(budget=latest_budget).values(
        'category', 
        'monthly_budget'
    )

    return JsonResponse({
        'expense_categories': list(expense_categories)
    })


# @require_GET
# def get_project_progress(request):
    
#     # You'll need to create a Project model for this
#     projects = Project.objects.all().values('name', 'progress')

#     return JsonResponse({
#         'projects': list(projects)
#     })



def profile(request):
    pass


