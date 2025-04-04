"""
Views for the employees app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Count
from .models import Employee, Title, GlobalSettings
from .forms import EmployeeCreationForm, EmployeeChangeForm, TitleForm, GlobalSettingsForm, EmployeeRegistrationForm
from attendance.models import Attendance, LeaveRequest, Notification

@login_required
def dashboard(request):
    """Dashboard view showing overview of attendance and leave."""
    # Get current user's attendance and leave data
    attendance_count = Attendance.objects.filter(employee=request.user).count()
    leave_pending = LeaveRequest.objects.filter(employee=request.user, status='pending').count()
    leave_approved = LeaveRequest.objects.filter(employee=request.user, status='approved').count()
    
    # For managers, get pending approvals
    pending_approvals = 0
    if Employee.objects.filter(manager=request.user).exists():
        pending_approvals = LeaveRequest.objects.filter(
            employee__manager=request.user, 
            status='pending'
        ).count()
    
    # Get unread notifications
    unread_notifications = Notification.objects.filter(
        user=request.user, 
        is_read=False
    ).order_by('-created_at')[:5]
    
    context = {
        'attendance_count': attendance_count,
        'leave_pending': leave_pending,
        'leave_approved': leave_approved,
        'pending_approvals': pending_approvals,
        'unread_notifications': unread_notifications,
        'holidays_left': request.user.holidays_left,
        'holidays_total': request.user.holidays_total,
    }
    
    return render(request, 'employees/dashboard.html', context)

@login_required
def employee_list(request):
    """View for listing all employees."""
    # Only admins can view all employees
    if not request.user.is_admin and not request.user.is_superuser:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('dashboard')
    
    employees = Employee.objects.all().order_by('first_name', 'last_name')
    
    context = {
        'employees': employees,
    }
    
    return render(request, 'employees/employee_list.html', context)

@login_required
def employee_detail(request, pk):
    """View for employee details."""
    employee = get_object_or_404(Employee, pk=pk)
    
    # Only admins or the employee themselves can view details
    if not request.user.is_admin and not request.user.is_superuser and request.user.pk != pk:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('dashboard')
    
    context = {
        'employee': employee,
    }
    
    return render(request, 'employees/employee_detail.html', context)

@login_required
def employee_create(request):
    """View for creating new employees."""
    # Only admins can create employees
    if not request.user.is_admin and not request.user.is_superuser:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.holidays_left = employee.holidays_total
            employee.save()
            messages.success(request, f"Employee {employee.get_full_name()} created successfully.")
            return redirect('employee_list')
    else:
        form = EmployeeCreationForm()
    
    context = {
        'form': form,
        'title': 'Add Employee',
    }
    
    return render(request, 'employees/employee_form.html', context)

@login_required
def employee_update(request, pk):
    """View for updating employees."""
    employee = get_object_or_404(Employee, pk=pk)
    
    # Only admins or the employee themselves can update
    if not request.user.is_admin and not request.user.is_superuser and request.user.pk != pk:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = EmployeeChangeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f"Employee {employee.get_full_name()} updated successfully.")
            if request.user.pk == pk:
                return redirect('profile')
            return redirect('employee_list')
    else:
        form = EmployeeChangeForm(instance=employee)
    
    context = {
        'form': form,
        'title': 'Edit Employee',
        'employee': employee,
    }
    
    return render(request, 'employees/employee_form.html', context)

@login_required
def profile(request):
    """View for user profile."""
    return employee_detail(request, request.user.pk)

@login_required
def title_list(request):
    """View for listing all titles."""
    # Only admins can view titles
    if not request.user.is_admin and not request.user.is_superuser:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('dashboard')
    
    titles = Title.objects.all().order_by('name')
    
    # Add count of employees with each title
    titles = titles.annotate(employee_count=Count('employee'))
    
    context = {
        'titles': titles,
    }
    
    return render(request, 'employees/title_list.html', context)

@login_required
def title_create(request):
    """View for creating new titles."""
    # Only admins can create titles
    if not request.user.is_admin and not request.user.is_superuser:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = TitleForm(request.POST)
        if form.is_valid():
            title = form.save()
            messages.success(request, f"Title '{title.name}' created successfully.")
            return redirect('title_list')
    else:
        form = TitleForm()
    
    context = {
        'form': form,
        'title': 'Add Title',
    }
    
    return render(request, 'employees/title_form.html', context)

@login_required
def title_update(request, pk):
    """View for updating titles."""
    # Only admins can update titles
    if not request.user.is_admin and not request.user.is_superuser:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('dashboard')
    
    title = get_object_or_404(Title, pk=pk)
    
    if request.method == 'POST':
        form = TitleForm(request.POST, instance=title)
        if form.is_valid():
            form.save()
            messages.success(request, f"Title '{title.name}' updated successfully.")
            return redirect('title_list')
    else:
        form = TitleForm(instance=title)
    
    context = {
        'form': form,
        'title': 'Edit Title',
    }
    
    return render(request, 'employees/title_form.html', context)

@login_required
def title_delete(request, pk):
    """View for deleting titles."""
    # Only admins can delete titles
    if not request.user.is_admin and not request.user.is_superuser:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('dashboard')
    
    title = get_object_or_404(Title, pk=pk)
    
    if request.method == 'POST':
        # Check if title is in use
        if Employee.objects.filter(title=title).exists():
            messages.error(request, f"Cannot delete title '{title.name}' as it is assigned to employees.")
            return redirect('title_list')
        
        title.delete()
        messages.success(request, f"Title '{title.name}' deleted successfully.")
        return redirect('title_list')
    
    context = {
        'title': title,
    }
    
    return render(request, 'employees/title_confirm_delete.html', context)

@login_required
def settings_update(request):
    """View for updating global settings."""
    # Only admins can update settings
    if not request.user.is_admin and not request.user.is_superuser:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('dashboard')
    
    settings = GlobalSettings.get_settings()
    
    if request.method == 'POST':
        form = GlobalSettingsForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Global settings updated successfully.")
            return redirect('settings')
    else:
        form = GlobalSettingsForm(instance=settings)
    
    context = {
        'form': form,
        'settings': settings,
    }
    
    return render(request, 'employees/settings_form.html', context)

@login_required
def notification_list(request):
    """View for listing user notifications."""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'notifications': notifications,
    }
    
    return render(request, 'employees/notification_list.html', context)

@login_required
def notification_mark_read(request, pk):
    """View for marking notifications as read."""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.mark_as_read()
    
    return redirect('notification_list')


def register(request):
    """View for employee self-registration."""
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = EmployeeRegistrationForm()
    
    return render(request, 'employees/register.html', {'form': form})
