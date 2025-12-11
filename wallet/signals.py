from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TopUpRequest
from skaagpay_backend.notification_service import send_to_user, send_to_admins

@receiver(post_save, sender=TopUpRequest)
def topup_notification(sender, instance, created, **kwargs):
    if created:
        # Notify Admins of new request
        send_to_admins(
            title="New TopUp Request",
            body=f"User {instance.user_phone} requested ₹{instance.amount}",
            data={'type': 'topup', 'id': str(instance.id)}
        )
    else:
        # Notify User of status change
        if instance.status == 'APPROVED':
            send_to_user(
                instance.user,
                title="TopUp Approved",
                body=f"Your wallet has been credited with ₹{instance.amount}",
                data={'type': 'topup', 'status': 'approved'}
            )
        elif instance.status == 'REJECTED':
            send_to_user(
                instance.user,
                title="TopUp Rejected",
                body="Your top-up request was rejected. Please contact support.",
                data={'type': 'topup', 'status': 'rejected'}
            )
