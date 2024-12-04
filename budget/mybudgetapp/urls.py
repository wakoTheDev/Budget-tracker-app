from django.urls import path
from . import views

urlpatterns = [
    path('',views.home),
    path('register',views.register,name='register'),
    path('login',views.login,name='login'),
    path('logout',views.logout,name='logout'),
    path('dashboard',views.user_dashboard,name='dashboard'),
    path('get_content/<str:page>/', views.get_content, name='get_content'),
    path('add_transaction',views.add_transaction,name='add_transaction'),
    path('add_scheduled_payment',views.add_transaction,name='add_scheduled_payment'),
]
