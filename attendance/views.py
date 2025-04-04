"""
Views for the attendance app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from datetime import datetime, timedelta
import json

from .models import Attendance, LeaveRequest, Notification
from .forms import AttendanceForm, LeaveRequestForm, LeaveApprovalForm
from employees.models import Employee, GlobalSettings

@login_required
def attendance_create(request):
    """View for recording attendance."""
    if request.method == 'POST':
        form = AttendanceForm(request.user, request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.employee = request.user
            attendance.save()
            messages.success(request, f"Attendance recorded for {attendance.date}.")
            return redirect('attendance_calendar')
    else:
        form = AttendanceForm(request.user, initial={'date': timezone.now().date()})
    
    context = {
        'form': form,
        'title': 'Record Attendance',
    }
    
    return render(request, 'attendance/attendance_form.html', context)

@login_required
def attendance_calendar(request):
    """View for attendance calendar."""
    # Get all attendance records for display in calendar
    attendances = Attendance.objects.all().select_related('employee')
    
    # Format data for FullCalendar
    events = []
    for attendance in attendances:
        events.append({
            'id': attendance.id,
            'title': f"{attendance.employee.get_full_name()} - {attendance.location}",
            'start': attendance.date.isoformat(),
            'end': attendance.date.isoformat(),
            'className': 'attendance-event',
            'extendedProps': {
                'employee': attendance.employee.get_full_name(),
                'location': attendance.location,
            }
        })
    
    context = {
        'events_json': json.dumps(events),
        'title': 'Attendance Calendar',
    }
    
    return render(request, 'attendance/attendance_calendar.html', context)

@login_required
def leave_request_create(request):
    """View for creating leave requests."""
    if request.method == 'POST':
        form = LeaveRequestForm(request.user, request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.employee = request.user
            leave_request.save()
            
            # Create notification for manager
            if request.user.manager:
                Notification.objects.create(
                    user=request.user.manager,
                    related_to=leave_request.id,
                    message=f"{request.user.get_full_name()} has requested leave from {leave_request.start_date} to {leave_request.end_date}."
                )
            
            messages.success(request, "Leave request submitted successfully.")
            return redirect('my_leave_requests')
    else:
        form = LeaveRequestForm(request.user)
    
    context = {
        'form': form,
        'title': 'Request Leave',
        'holidays_left': request.user.holidays_left,
    }
    
    return render(request, 'attendance/leave_request_form.html', context)

@login_required
def leave_calendar(request):
    """View for leave calendar."""
    # Get all leave requests for display in calendar
    leave_requests = LeaveRequest.objects.filter(
        status__in=['approved', 'pending']
    ).select_related('employee')
    
    # Format data for FullCalendar
    events = []
    for leave in leave_requests:
        # Set color based on status
        color = '#ffc107' if leave.status == 'pending' else '#28a745'
        
        events.append({
            'id': leave.id,
            'title': f"{leave.employee.get_full_name()} - {leave.get_status_display()}",
            'start': leave.start_date.isoformat(),
            'end': (leave.end_date + timedelta(days=1)).isoformat(),  # Add 1 day to make it inclusive
            'color': color,
            'className': f"leave-event leave-{leave.status}",
            'extendedProps': {
                'employee': leave.employee.get_full_name(),
                'status': leave.get_status_display(),
                'reason': leave.reason,
            }
        })
    
    context = {
        'events_json': json.dumps(events),
        'title': 'Leave Calendar',
    }
    
    return render(request, 'attendance/leave_calendar.html', context)

@login_required
def combined_calendar(request):
    """View for combined attendance and leave calendar."""
    # Get all attendance records
    attendances = Attendance.objects.all().select_related('employee')
    
    # Get all leave requests
    leave_requests = LeaveRequest.objects.filter(
        status__in=['approved', 'pending']
    ).select_related('employee')
    
    # Format data for FullCalendar
    events = []
    
    # Add attendance events
    for attendance in attendances:
        events.append({
            'id': f"attendance_{attendance.id}",
            'title': f"{attendance.employee.get_full_name()} - {attendance.location}",
            'start': attendance.date.isoformat(),
            'end': attendance.date.isoformat(),
            'className': 'attendance-event',
            'color': '#17a2b8',  # Info color
            'extendedProps': {
                'type': 'attendance',
                'employee': attendance.employee.get_full_name(),
                'location': attendance.location,
            }
        })
    
    # Add leave events
    for leave in leave_requests:
        # Set color based on status
        color = '#ffc107' if leave.status == 'pending' else '#28a745'
        
        events.append({
            'id': f"leave_{leave.id}",
            'title': f"{leave.employee.get_full_name()} - Leave ({leave.get_status_display()})",
            'start': leave.start_date.isoformat(),
            'end': (leave.end_date + timedelta(days=1)).isoformat(),  # Add 1 day to make it inclusive
            'color': color,
            'className': f"leave-event leave-{leave.status}",
            'extendedProps': {
                'type': 'leave',
                'employee': leave.employee.get_full_name(),
                'status': leave.get_status_display(),
                'reason': leave.reason,
            }
        })
    
    context = {
        'events_json': json.dumps(events),
        'title': 'Combined Calendar',
    }
    
    return render(request, 'attendance/combined_calendar.html', context)

@login_required
def my_leave_requests(request):
    """View for listing user's leave requests."""
    leave_requests = LeaveRequest.objects.filter(employee=request.user).order_by('-created_at')
    
    context = {
        'leave_requests': leave_requests,
        'title': 'My Leave Requests',
    }
    
    return render(request, 'attendance/my_leave_requests.html', context)

@login_required
def pending_leave_approvals(request):
    """View for listing pending leave approvals for managers."""
    # Check if user is a manager
    if not Employee.objects.filter(manager=request.user).exists():
        messages.error(request, "You don't have permission to view this page.")
        return redirect('dashboard')
    
    pending_requests = LeaveRequest.objects.filter(
        employee__manager=request.user,
        status='pending'
    ).order_by('-created_at')
    
    context = {
        'pending_requests': pending_requests,
        'title': 'Pending Leave Approvals',
    }
    
    return render(request, 'attendance/pending_leave_approvals.html', context)

@login_required
def leave_request_approve(request, pk):
    """View for approving or rejecting leave requests."""
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    # Check if user is the manager of the employee
    if request.user != leave_request.employee.manager:
        messages.error(request, "You don't have permission to approve this leave request.")
        return redirect('dashboard')
    
    # Check if request is still pending
    if leave_request.status != 'pending':
        messages.error(request, "This leave request has already been processed.")
        return redirect('pending_leave_approvals')
    
    if request.method == 'POST':
        form = LeaveApprovalForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            
            if action == 'approve':
                leave_request.approve(request.user)
                messages.success(request, "Leave request approved successfully.")
            else:
                leave_request.reject(request.user)
                messages.success(request, "Leave request rejected successfully.")
            
            return redirect('pending_leave_approvals')
    else:
        form = LeaveApprovalForm()
    
    context = {
        'form': form,
        'leave_request': leave_request,
        'title': 'Approve Leave Request',
    }
    
    return render(request, 'attendance/leave_approval_form.html', context)

@login_required
def leave_request_cancel(request, pk):
    """View for canceling leave requests."""
    leave_request = get_object_or_404(LeaveRequest, pk=pk, employee=request.user)
    
    # Check if request can be canceled (only pending or future approved requests)
    if leave_request.status == 'rejected':
        messages.error(request, "Cannot cancel a rejected leave request.")
        return redirect('my_leave_requests')
    
    if leave_request.status == 'approved' and leave_request.start_date <= timezone.now().date():
        messages.error(request, "Cannot cancel an approved leave request that has already started.")
        return redirect('my_leave_requests')
    
    if request.method == 'POST':
        # If approved, restore holidays
        if leave_request.status == 'approved':
            days = (leave_request.end_date - leave_request.start_date).days + 1
            leave_request.employee.holidays_left += days
            leave_request.employee.save()
        
        # Delete the leave request
        leave_request.delete()
        
        messages.success(request, "Leave request canceled successfully.")
        return redirect('my_leave_requests')
    
    context = {
        'leave_request': leave_request,
        'title': 'Cancel Leave Request',
    }
    
    return render(request, 'attendance/leave_cancel_confirm.html', context)

@login_required
def reports(request):
    """View for reports dashboard."""
    # Only admins can view reports
    if not request.user.is_admin and not request.user.is_superuser:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('dashboard')
    
    context = {
        'title': 'Reports',
    }
    
    return render(request, 'attendance/reports.html', context)

@login_required
def attendance_report(request):
    """View for attendance reports."""
    # Only admins can view reports
    if not request.user.is_admin and not request.user.is_superuser:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('dashboard')
    
    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    employee_id = request.GET.get('employee_id')
    location = request.GET.get('location')
    
    # Base queryset
    attendances = Attendance.objects.all().select_related('employee')
    
    # Apply filters
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            attendances = attendances.filter(date__gte=start_date)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            attendances = attendances.filter(date__lte=end_date)
        except ValueError:
            pass
    
    if employee_id:
        attendances = attendances.filter(employee_id=employee_id)
    
    if location:
        attendances = attendances.filter(location__icontains=location)
    
    # Order by date
    attendances = attendances.order_by('-date')
    
    # Get all employees for filter dropdown
    employees = Employee.objects.all().order_by('first_name', 'last_name')
    
    context = {
        'attendances': attendances,
        'employees': employees,
        'title': 'Attendance Report',
        'filters': {
            'start_date': start_date,
            'end_date': end_date,
            'employee_id': employee_id,
            'location': location,
        }
    }
    
    return render(request, 'attendance/attendance_report.html', context)

@login_required
def leave_report(request):
    """View for leave reports."""
    # Only admins can view reports
    if not request.user.is_admin and not request.user.is_superuser:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('dashboard')
    
    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    employee_id = request.GET.get('employee_id')
    status = request.GET.get('status')
    
    # Base queryset
    leave_requests = LeaveRequest.objects.all().select_related('employee', 'manager')
    
    # Apply filters
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            leave_requests = leave_requests.filter(
                Q(start_date__gte=start_date) | Q(end_date__gte=start_date)
            )
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            leave_requests = leave_requests.filter(
                Q(start_date__lte=end_date) | Q(end_date__lte=end_date)
            )
        except ValueError:
            pass
    
    if employee_id:
        leave_requests = leave_requests.filter(employee_id=employee_id)
    
    if status:
        leave_requests = leave_requests.filter(status=status)
    
    # Order by created_at
    leave_requests = leave_requests.order_by('-created_at')
    
    # Get all employees for filter dropdown
    employees = Employee.objects.all().order_by('first_name', 'last_name')
    
    context = {
        'leave_requests': leave_requests,
        'employees': employees,
        'title': 'Leave Report',
        'filters': {
            'start_date': start_date,
            'end_date': end_date,
            'employee_id': employee_id,
            'status': status,
        },
        'status_choices': LeaveRequest.STATUS_CHOICES,
    }
    
    return render(request, 'attendance/leave_report.html', context)

from django.http import JsonResponse
from datetime import datetime
import json

def dashboard_events_api(request) :
    """API endpoint for dashboard calendar events."""
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    
    # Convert string dates to datetime objects if provided
    if start_date:
        start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    if end_date:
        end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    
    # Get attendance records
    attendance_records = Attendance.objects.filter(employee=request.user)
    if start_date:
        attendance_records = attendance_records.filter(date__gte=start_date)
    if end_date:
        attendance_records = attendance_records.filter(date__lte=end_date)
    
    # Get leave requests
    leave_requests = LeaveRequest.objects.filter(employee=request.user)
    if start_date:
        leave_requests = leave_requests.filter(end_date__gte=start_date)
    if end_date:
        leave_requests = leave_requests.filter(start_date__lte=end_date)
    
    # Format events for calendar
    events = []
    
    # Add attendance records
    for record in attendance_records:
        events.append({
            'id': f'attendance_{record.id}',
            'title': 'Present' if record.is_present else 'Absent',
            'start': record.date.isoformat(),
            'end': record.date.isoformat(),
            'color': '#28a745' if record.is_present else '#dc3545',
            'type': 'attendance'
        })
    
    # Add leave requests
    for leave in leave_requests:
        status_colors = {
            'pending': '#ffc107',
            'approved': '#28a745',
            'rejected': '#dc3545',
            'cancelled': '#6c757d'
        }
        events.append({
            'id': f'leave_{leave.id}',
            'title': f'{leave.leave_type} ({leave.status})',
            'start': leave.start_date.isoformat(),
            'end': leave.end_date.isoformat(),
            'color': status_colors.get(leave.status, '#007bff'),
            'type': 'leave'
        })
    
    return JsonResponse(events, safe=False)

