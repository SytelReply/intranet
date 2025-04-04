"""
Models for the attendance app.
"""
from django.db import models
from django.utils import timezone
from employees.models import Employee

class Attendance(models.Model):
    """Model for employee attendance records."""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['employee', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.employee} - {self.date} - {self.location}"


class LeaveRequest(models.Model):
    """Model for employee leave requests."""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='leave_approvals')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee} - {self.start_date} to {self.end_date} - {self.status}"

    def approve(self, manager):
        """Approve leave request and update employee's holidays left."""
        if self.status == 'pending':
            self.status = 'approved'
            self.manager = manager
            self.approved_at = timezone.now()
            
            # Calculate number of days
            days = (self.end_date - self.start_date).days + 1
            
            # Update employee's holidays left
            self.employee.holidays_left -= days
            self.employee.save()
            
            self.save()
            
            # Create notification
            Notification.objects.create(
                user=self.employee,
                related_to=self.id,
                message=f"Your leave request from {self.start_date} to {self.end_date} has been approved."
            )
            
            return True
        return False

    def reject(self, manager):
        """Reject leave request."""
        if self.status == 'pending':
            self.status = 'rejected'
            self.manager = manager
            self.approved_at = timezone.now()
            self.save()
            
            # Create notification
            Notification.objects.create(
                user=self.employee,
                related_to=self.id,
                message=f"Your leave request from {self.start_date} to {self.end_date} has been rejected."
            )
            
            return True
        return False


class Notification(models.Model):
    """Model for system notifications."""
    user = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='notifications')
    related_to = models.IntegerField(null=True, blank=True)  # ID of related entity
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def mark_as_read(self):
        """Mark notification as read."""
        self.is_read = True
        self.save()
