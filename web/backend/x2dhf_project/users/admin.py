from django.contrib import admin
from .models import UserProfile,Subscription,APIAuditLog
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display=['user','organization','plan','subscription_active','storage_used_gb','monthly_computations']
    list_filter=['plan','subscription_active']
    search_fields=['user__username','organization']
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display=['user','plan','status','current_period_start','current_period_end']
    list_filter=['plan','status']
    search_fields=['user__username']
@admin.register(APIAuditLog)
class APIAuditLogAdmin(admin.ModelAdmin):
    list_display=['user','endpoint','method','status_code','ip_address','timestamp']
    list_filter=['method','status_code','timestamp']
    search_fields=['user__username','endpoint','ip_address']
    readonly_fields=['timestamp']
