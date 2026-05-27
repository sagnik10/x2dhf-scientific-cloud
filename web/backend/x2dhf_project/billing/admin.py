from django.contrib import admin
from .models import Invoice,Payment,Usage,PricingPlan,LineItem
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display=['invoice_number','user','amount_due','status','issue_date']
    list_filter=['status','issue_date']
    search_fields=['invoice_number','user__username']
    readonly_fields=['created_at','updated_at']
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display=['stripe_payment_id','user','amount','status','created_at']
    list_filter=['status','payment_method','created_at']
    search_fields=['stripe_payment_id','user__username']
    readonly_fields=['created_at','updated_at']
@admin.register(Usage)
class UsageAdmin(admin.ModelAdmin):
    list_display=['user','computations_this_month','storage_used_gb','api_calls_this_month']
    search_fields=['user__username']
@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    list_display=['name','slug','monthly_price','max_computations','storage_gb']
    search_fields=['name','slug']
    readonly_fields=['created_at']
@admin.register(LineItem)
class LineItemAdmin(admin.ModelAdmin):
    list_display=['invoice','description','quantity','unit_price','total']
    search_fields=['invoice__invoice_number','description']
