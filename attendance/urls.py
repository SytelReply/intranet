"""
URLs configuration for the attendance app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Attendance management
    path('record/', views.attendance_create, name='attendance_create'),
    path('calendar/', views.attendance_calendar, name='attendance_calendar'),
    
    # Leave management
    path('leave/request/', views.leave_request_create, name='leave_request_create'),
    path('leave/calendar/', views.leave_calendar, name='leave_calendar'),
    path('leave/my-requests/', views.my_leave_requests, name='my_leave_requests'),
    path('leave/pending-approvals/', views.pending_leave_approvals, name='pending_leave_approvals'),
    path('leave/<int:pk>/approve/', views.leave_request_approve, name='leave_request_approve'),
    path('leave/<int:pk>/cancel/', views.leave_request_cancel, name='leave_request_cancel'),
    
    # Combined calendar
    path('combined-calendar/', views.combined_calendar, name='combined_calendar'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
    path('reports/attendance/', views.attendance_report, name='attendance_report'),
    path('reports/leave/', views.leave_report, name='leave_report'),

    # API endpoints
    path('api/dashboard-events/', views.dashboard_events_api, name='dashboard_events_api'),
]
