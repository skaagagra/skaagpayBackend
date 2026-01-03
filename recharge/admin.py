from django.contrib import admin
from .models import RechargeRequest, Operator, Plan

@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_default')
    list_filter = ('category', 'is_default')
    search_fields = ('name',)


@admin.register(RechargeRequest)
class RechargeRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'mobile_number', 'operator', 'amount', 'platform_fee', 'total_amount', 'status', 'created_at')
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

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('operator', 'amount', 'data', 'validity', 'plan_type', 'circle', 'talktime', 'created_at')
    list_filter = ('operator', 'plan_type', 'circle', 'created_at')
    search_fields = ('operator__name', 'plan_type', 'circle')
