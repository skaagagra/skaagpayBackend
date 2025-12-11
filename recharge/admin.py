from django.contrib import admin
from .models import RechargeRequest

@admin.register(RechargeRequest)
class RechargeRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'mobile_number', 'operator', 'amount', 'status', 'created_at')
    list_filter = ('status', 'operator', 'created_at')
    search_fields = ('user__phone_number', 'mobile_number')
    list_editable = ('status',) # Allow admin to quickly change status from list view

    def save_model(self, request, obj, form, change):
        if change:
            original_obj = RechargeRequest.objects.get(pk=obj.pk)
            if original_obj.status != obj.status:
                # Notify User
                from common.notifications import send_user_notification
                send_user_notification(
                    user=obj.user,
                    title=f"Recharge {obj.status}",
                    body=f"Your recharge for {obj.mobile_number} is now {obj.status}."
                )
        super().save_model(request, obj, form, change)
