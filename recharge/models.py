from django.db import models
from django.conf import settings

class RechargeRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('SCHEDULED', 'Scheduled'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recharge_requests')
    mobile_number = models.CharField(max_length=15)
    operator = models.CharField(max_length=50) # In real app, this might be a ForeignKey to an Operator model
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_scheduled = models.BooleanField(default=False)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Recharge: {self.mobile_number} ({self.operator}) - {self.amount} - {self.status}"
