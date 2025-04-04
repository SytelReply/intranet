"""
Admin configuration for the employees app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Employee, Title, GlobalSettings

@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
    """Admin configuration for Employee model."""
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'mobile', 'title', 'manager')}),
        (_('Holiday info'), {'fields': ('holidays_total', 'holidays_left')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_admin', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'title', 'holidays_left', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_admin', 'title')


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    """Admin configuration for Title model."""
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    """Admin configuration for GlobalSettings model."""
    list_display = ('company_name', 'max_rollover', 'updated_at')
    
    def has_add_permission(self, request):
        # Only allow one instance of GlobalSettings
        return not GlobalSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the settings
        return False

    def has_add_permission(self, request):
        # Only allow one instance
        return not GlobalSettings.objects.exists()
