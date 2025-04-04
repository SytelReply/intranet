"""
Forms for the employees app.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Employee, Title, GlobalSettings

class EmployeeCreationForm(UserCreationForm):
    """Form for creating new employees."""
    
    class Meta:
        model = Employee
        fields = ('email', 'first_name', 'last_name', 'mobile', 'title', 'holidays_total', 'manager')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['mobile'].widget.attrs.update({'class': 'form-control'})
        self.fields['title'].widget.attrs.update({'class': 'form-select'})
        self.fields['holidays_total'].widget.attrs.update({'class': 'form-control'})
        self.fields['manager'].widget.attrs.update({'class': 'form-select'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})


class EmployeeChangeForm(UserChangeForm):
    """Form for updating employees."""
    
    class Meta:
        model = Employee
        fields = ('email', 'first_name', 'last_name', 'mobile', 'title', 'holidays_total', 'holidays_left', 'manager', 'is_admin')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['mobile'].widget.attrs.update({'class': 'form-control'})
        self.fields['title'].widget.attrs.update({'class': 'form-select'})
        self.fields['holidays_total'].widget.attrs.update({'class': 'form-control'})
        self.fields['holidays_left'].widget.attrs.update({'class': 'form-control'})
        self.fields['manager'].widget.attrs.update({'class': 'form-select'})
        self.fields['is_admin'].widget.attrs.update({'class': 'form-check-input'})


class LoginForm(AuthenticationForm):
    """Custom login form."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})


class TitleForm(forms.ModelForm):
    """Form for creating and updating titles."""
    
    class Meta:
        model = Title
        fields = ('name',)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})


class GlobalSettingsForm(forms.ModelForm):
    """Form for updating global settings."""
    
    class Meta:
        model = GlobalSettings
        fields = ('company_name', 'company_logo', 'max_rollover')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['company_logo'].widget.attrs.update({'class': 'form-control'})
        self.fields['max_rollover'].widget.attrs.update({'class': 'form-control'})
    
    def clean_max_rollover(self):
        """Validate max_rollover field."""
        max_rollover = self.cleaned_data.get('max_rollover')
        if max_rollover < 0:
            raise ValidationError("Maximum rollover days cannot be negative.")
        return max_rollover


class EmployeeRegistrationForm(forms.ModelForm):
    """Form for employee self-registration."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    
    class Meta:
        model = Employee
        fields = ['email', 'first_name', 'last_name', 'mobile', 'title', 'manager']
        
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match')
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
