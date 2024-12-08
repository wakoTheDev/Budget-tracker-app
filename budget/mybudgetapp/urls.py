from django.urls import path
from . import views

urlpatterns = [
    path('',views.home),
    path('register',views.register,name='register'),
    path('login',views.login,name='login'),
    path('logout',views.logout,name='logout'),
    path('dashboard',views.user_dashboard,name='dashboard'),
    path('get_content/<str:page>/', views.get_content, name='get_content'),
    path('get_nav_content/<str:page>/', views.get_nav_content, name='get_nav_content'),
    path('limit-form/', views.limit_form, name='limit_form'),
    path('set_account_limits/', views.set_account_limits, name='set_account_limits'),
    path('scheduler',views.scheduler,name='scheduler'),
    path('get_schedules/', views.get_schedules, name='get_schedules'),
    path('add_scheduled_payment',views.add_payment_schedule,name='add_scheduled_payment'),
    path('delete_schedule/<uuid:schedule_id>/', views.delete_schedule, name='delete_schedule'),
    path('update_schedule/<uuid:schedule_id>/', views.update_schedule, name='update_schedule'),
    path('back_to_schedule',views.back_to_schedule,name="back_to_schedule"),
    path('api/upcoming-schedules/', views.get_upcoming_schedules, name='upcoming-schedules'),
]
