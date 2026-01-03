from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import RechargeRequest
from wallet.models import Wallet, Transaction
from django.db import transaction as db_transaction

# Use Pre Save to detect Status Change
@receiver(pre_save, sender=RechargeRequest)
def recharge_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = RechargeRequest.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except RechargeRequest.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None

@receiver(post_save, sender=RechargeRequest)
def recharge_notification(sender, instance, created, **kwargs):
    # Determine if status changed to FAILED
    status_changed_to_failed = False
    if not created and hasattr(instance, '_old_status'):
        if instance._old_status != 'FAILED' and instance.status == 'FAILED':
            status_changed_to_failed = True

    if status_changed_to_failed:
         # PROCESS REFUND
         with db_transaction.atomic():
             wallet, _ = Wallet.objects.get_or_create(user=instance.user)
             refund_amount = instance.total_amount if instance.total_amount > 0 else instance.amount
             
             # Prevent double refund if already refunded (logic check)
             # Ideally we check transaction logs, but for now simple status check is our guard.
             
             wallet.balance = float(wallet.balance) + float(refund_amount)
             wallet.save()
             
             Transaction.objects.create(
                 wallet=wallet,
                 amount=refund_amount,
                 transaction_type='CREDIT',
                 description=f"Refund for Rej/Failed Recharge: {instance.mobile_number}"
             )

    # Notifications
    from skaagpay_backend.notification_service import send_to_user, send_to_admins
    
    if created:
        # Notify Admins of new recharge
        send_to_admins(
            title="New Recharge",
            body=f"{instance.mobile_number} - ₹{instance.amount}",
            data={'type': 'recharge', 'id': str(instance.id)}
        )
    else:
        # Notify User of status change
        if instance.status == 'SUCCESS':
            send_to_user(
                instance.user,
                title="Recharge Successful",
                body=f"Recharge of ₹{instance.amount} for {instance.mobile_number} was successful.",
                data={'type': 'recharge', 'status': 'success'}
            )
        elif instance.status == 'FAILED':
             # Notification
             pass # Handled by the generic below or explicit?
             send_to_user(
                instance.user,
                title="Recharge Failed",
                body=f"Recharge of ₹{instance.amount} failed. Refund of ₹{instance.total_amount if instance.total_amount > 0 else instance.amount} processed.",
                data={'type': 'recharge', 'status': 'failed'}
            )
