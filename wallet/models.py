from django.db import models
from django.conf import settings

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.user.phone_number}'s Wallet ({self.balance})"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('CREDIT', 'Credit'),
        ('DEBIT', 'Debit'),
        ('TRANSFER_SENT', 'Transfer Sent'),
        ('TRANSFER_RECEIVED', 'Transfer Received'),
    )
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255)
    
    # New fields for better UI
    status = models.CharField(max_length=20, default='SUCCESS') # SUCCESS, PENDING, FAILED
    operator_name = models.CharField(max_length=100, blank=True, null=True)
    operator_logo = models.URLField(max_length=500, blank=True, null=True)
    target_number = models.CharField(max_length=100, blank=True, null=True)
    target_name = models.CharField(max_length=100, blank=True, null=True)
    
    # Links to original requests
    recharge_request = models.ForeignKey('recharge.RechargeRequest', on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    topup_request = models.ForeignKey('wallet.TopUpRequest', on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} for {self.wallet.user.phone_number}"

class TopUpRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='topup_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_reference = models.CharField(max_length=4, default='0000', help_text="Last 4 digits of Transaction ID")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    admin_note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"TopUp Request: {self.amount} by {self.user.phone_number} - {self.status}"
