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
    CATEGORY_CHOICES = (
        ('MOBILE_PREPAID', 'Mobile Prepaid'),
        ('MOBILE_POSTPAID', 'Mobile Postpaid'),
        ('DTH', 'DTH'),
        ('BROADBAND', 'Broadband'),
        ('ELECTRICITY', 'Electricity'),
        ('GAS', 'Gas'),
        ('WATER', 'Water'),
        ('OTHER', 'Other'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recharge_requests')
    mobile_number = models.CharField(max_length=30) # Increased to support various consumer IDs
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='MOBILE_PREPAID')
    operator = models.CharField(max_length=50) # In real app, this might be a ForeignKey to an Operator model
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_scheduled = models.BooleanField(default=False)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Recharge: {self.mobile_number} ({self.operator}) - {self.amount} - {self.status}"

class Operator(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=RechargeRequest.CATEGORY_CHOICES)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.category})"

class Plan(models.Model):
    PLAN_TYPES = (
        ('TOPUP', 'Topup'),
        ('DATA', 'Data'),
        ('SMS', 'SMS'),
        ('UNLIMITED', 'Unlimited'),
        ('ROAMING', 'Roaming'),
        ('OTHER', 'Other'),
    )
    
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, related_name='plans')
    amount = models.DecimalField(max_digits=10, decimal_places=2) # Price
    data = models.CharField(max_length=500, blank=True, null=True) # Data
    validity = models.CharField(max_length=500, blank=True, null=True) # Validity
    additional_benefits = models.TextField(blank=True, null=True) # Additional Benefits
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, default='OTHER')
    
    # Optional fields for future proofing or explicit filtering
    circle = models.CharField(max_length=100, default='ALL') 
    talktime = models.CharField(max_length=500, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.operator.name} - {self.amount}"
