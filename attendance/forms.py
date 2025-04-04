"""
Forms for the attendance app.
"""
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Attendance, LeaveRequest
from employees.models import Employee

class AttendanceForm(forms.ModelForm):
    """Form for creating and updating attendance records."""
    
    class Meta:
        model = Attendance
        fields = ('date', 'location')
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'location': forms.TextInput(attrs={'class': 'form-control'})
        }
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
    
    def clean_date(self):
        """Validate date field."""
        date = self.cleaned_data.get('date')
        if date < timezone.now().date():
            raise ValidationError("You cannot record attendance for past dates.")
        
        # Check if attendance already exists for this date
        if self.user and not self.instance.pk:
            if Attendance.objects.filter(employee=self.user, date=date).exists():
                raise ValidationError("You have already recorded attendance for this date.")
        
        return date


class LeaveRequestForm(forms.ModelForm):
    """Form for creating leave requests."""
    
    class Meta:
        model = LeaveRequest
        fields = ('start_date', 'end_date', 'reason')
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
    
    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            # Ensure end_date is not before start_date
            if end_date < start_date:
                raise ValidationError("End date cannot be before start date.")
            
            # Ensure start_date is not in the past
            if start_date < timezone.now().date():
                raise ValidationError("Start date cannot be in the past.")
            
            # Calculate number of days
            days = (end_date - start_date).days + 1
            
            # Check if employee has enough holidays left
            if self.user and days > self.user.holidays_left:
                raise ValidationError(f"You don't have enough holidays left. You requested {days} days but only have {self.user.holidays_left} days available.")
            
            # Check for overlapping leave requests
            if self.user and not self.instance.pk:
                overlapping = LeaveRequest.objects.filter(
                    employee=self.user,
                    status__in=['pending', 'approved'],
                ).filter(
                    # Either start_date or end_date falls within the requested period
                    # or the requested period is completely within an existing leave request
                    models.Q(start_date__lte=end_date, end_date__gte=start_date) |
                    models.Q(start_date__gte=start_date, end_date__lte=end_date)
                ).exists()
                
                if overlapping:
                    raise ValidationError("This leave request overlaps with an existing request.")
        
        return cleaned_data


class LeaveApprovalForm(forms.Form):
    """Form for approving or rejecting leave requests."""
    
    action = forms.ChoiceField(
        choices=[('approve', 'Approve'), ('reject', 'Reject')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['action'].initial = 'approve'
