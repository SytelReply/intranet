"""
Admin configuration for the attendance app.
"""
from django.contrib import admin
from .models import Attendance, LeaveRequest, Notification

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Admin configuration for Attendance model."""
    list_display = ('employee', 'date', 'location', 'created_at')
    list_filter = ('date', 'location')
    search_fields = ('employee__first_name', 'employee__last_name', 'location')
    date_hierarchy = 'date'


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    """Admin configuration for LeaveRequest model."""
    list_display = ('employee', 'start_date', 'end_date', 'status', 'manager', 'created_at')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('employee__first_name', 'employee__last_name', 'reason')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'approved_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin configuration for Notification model."""
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'message')
    date_hierarchy = 'created_at'
