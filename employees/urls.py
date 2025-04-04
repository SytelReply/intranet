"""
URLs configuration for the employees app.
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import LoginForm

urlpatterns = [
    # Authentication
    path('login/', auth_views.LoginView.as_view(
        template_name='employees/login.html',
        authentication_form=LoginForm
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='employees/password_change.html',
        success_url='/password_change/done/'
    ), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='employees/password_change_done.html'
    ), name='password_change_done'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Employee management
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/edit/', views.employee_update, name='employee_update'),
    
    # Title management
    path('titles/', views.title_list, name='title_list'),
    path('titles/add/', views.title_create, name='title_create'),
    path('titles/<int:pk>/edit/', views.title_update, name='title_update'),
    path('titles/<int:pk>/delete/', views.title_delete, name='title_delete'),
    
    # Settings
    path('settings/', views.settings_update, name='settings'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    
    # Notifications
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:pk>/mark-read/', views.notification_mark_read, name='notification_mark_read'),

    path('register/', views.register, name='register'),
]
