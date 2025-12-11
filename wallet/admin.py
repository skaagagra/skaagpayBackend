from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.db import transaction as db_transaction
from .models import Wallet, Transaction, TopUpRequest

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')
    search_fields = ('user__phone_number', 'user__full_name')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'amount', 'transaction_type', 'description', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('wallet__user__phone_number',)

@admin.register(TopUpRequest)
class TopUpRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'display_screenshot', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__phone_number', 'user__full_name')
    readonly_fields = ('display_screenshot',)

    def display_screenshot(self, obj):
        if obj.screenshot:
            return format_html('<a href="{}" target="_blank"><img src="{}" width="100" height="100" /></a>', obj.screenshot.url, obj.screenshot.url)
        return "No Screenshot"
    display_screenshot.short_description = 'Payment Screenshot'

    def save_model(self, request, obj, form, change):
        # Handle status change logic
        if change: # If updating existing object
            original_obj = TopUpRequest.objects.get(pk=obj.pk)
            if original_obj.status == 'PENDING' and obj.status == 'APPROVED':
                # Credit the wallet
                with db_transaction.atomic():
                    wallet, created = Wallet.objects.get_or_create(user=obj.user)
                    wallet.balance += obj.amount
                    wallet.save()
                    
                    Transaction.objects.create(
                        wallet=wallet,
                        amount=obj.amount,
                        transaction_type='CREDIT',
                        description=f"TopUp Approved: {obj.pk}"
                    )
                    messages.success(request, f"Wallet credited with {obj.amount}")
                
                    # Notify User
                    from common.notifications import send_user_notification
                    send_user_notification(
                        user=obj.user,
                        title="Top-Up Approved",
                        body=f"Your wallet has been credited with {obj.amount}"
                    )
            
            elif original_obj.status == 'APPROVED' and obj.status != 'APPROVED':
                 messages.warning(request, "Caution: Changing status from Approved does NOT revert the balance automatically.")

        super().save_model(request, obj, form, change)
