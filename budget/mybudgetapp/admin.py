from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Customer)
admin.site.register(PaymentSchedule)
admin.site.register(Account)
admin.site.register(Limit)
admin.site.register(WeeklyBudget)