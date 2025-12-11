from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction as db_transaction
from recharge.models import RechargeRequest
from wallet.models import Wallet, Transaction

class Command(BaseCommand):
    help = 'Process scheduled recharges that are due'

    def handle(self, *args, **options):
        now = timezone.now()
        due_recharges = RechargeRequest.objects.filter(
            status='SCHEDULED',
            scheduled_at__lte=now
        )

        self.stdout.write(f"Found {due_recharges.count()} due recharges.")

        for recharge in due_recharges:
            with db_transaction.atomic():
                user = recharge.user
                wallet, created = Wallet.objects.get_or_create(user=user)

                if wallet.balance >= recharge.amount:
                    # Deduct
                    wallet.balance -= recharge.amount
                    wallet.save()

                    # Log Tx
                    Transaction.objects.create(
                        wallet=wallet,
                        amount=recharge.amount,
                        transaction_type='DEBIT',
                        description=f"Scheduled Recharge processed for {recharge.mobile_number}"
                    )

                    recharge.status = 'PENDING' # Or SUCCESS
                    recharge.save()
                    
                    # Notify User
                    from common.notifications import send_user_notification
                    send_user_notification(
                        user=user,
                        title="Scheduled Recharge Processed",
                        body=f"Recharge for {recharge.mobile_number} of {recharge.amount} is now PENDING/SUCCESS."
                    )
                    
                    self.stdout.write(self.style.SUCCESS(f"Processed recharge {recharge.id} for {user.phone_number}"))
                else:
                    recharge.status = 'FAILED'
                    recharge.save()

                    # Notify User
                    from common.notifications import send_user_notification
                    send_user_notification(
                        user=user,
                        title="Scheduled Recharge Failed",
                        body=f"Insufficient balance for scheduled recharge of {recharge.amount}"
                    )

                    self.stdout.write(self.style.ERROR(f"Failed recharge {recharge.id} due to insufficient funds"))
