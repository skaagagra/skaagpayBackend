from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RechargeRequest
from skaagpay_backend.notification_service import send_to_user, send_to_admins

@receiver(post_save, sender=RechargeRequest)
def recharge_notification(sender, instance, created, **kwargs):
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
            send_to_user(
                instance.user,
                title="Recharge Failed",
                body=f"Recharge of ₹{instance.amount} failed. Amount refunded.",
                data={'type': 'recharge', 'status': 'failed'}
            )
