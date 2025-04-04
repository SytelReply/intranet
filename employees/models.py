"""
Models for the employees app.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class EmployeeManager(BaseUserManager):
    """Define a model manager for Employee model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class Title(models.Model):
    """Model for employee titles."""
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Employee(AbstractUser):
    """Custom user model for employees."""
    username = None
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    mobile = models.CharField(max_length=20, blank=True)
    title = models.ForeignKey(Title, on_delete=models.SET_NULL, null=True, blank=True)
    holidays_total = models.PositiveIntegerField(default=25)
    holidays_left = models.PositiveIntegerField(default=25)
    is_admin = models.BooleanField(default=False)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='team_members')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = EmployeeManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class GlobalSettings(models.Model):
    """Model for global application settings."""
    max_rollover = models.PositiveIntegerField(default=5)
    company_name = models.CharField(max_length=100, default="NetReply")
    company_logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    default_holidays = models.PositiveIntegerField(default=25, help_text="Default number of holidays for all employees")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Global Settings"

    def __str__(self):
        return self.company_name

    @classmethod
    def get_settings(cls):
        """Get or create global settings."""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
