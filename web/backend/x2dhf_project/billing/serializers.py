from rest_framework import serializers
from .models import Invoice,Payment,Usage,PricingPlan,LineItem
class LineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=LineItem
        fields=['id','description','quantity','unit_price','total']
class InvoiceSerializer(serializers.ModelSerializer):
    items=LineItemSerializer(many=True,read_only=True)
    class Meta:
        model=Invoice
        fields=['id','invoice_number','status','amount_due','amount_paid','currency','issue_date','due_date','paid_date','items','created_at','updated_at']
        read_only_fields=['id','invoice_number','issue_date','created_at','updated_at']
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Payment
        fields=['id','invoice','amount','currency','status','payment_method','created_at','updated_at']
        read_only_fields=['id','stripe_payment_id','created_at','updated_at']
class UsageSerializer(serializers.ModelSerializer):
    class Meta:
        model=Usage
        fields=['id','computations_this_month','storage_used_gb','api_calls_this_month','gpu_hours_this_month','reset_date']
        read_only_fields=['id','computations_this_month','storage_used_gb','api_calls_this_month','gpu_hours_this_month','reset_date']
class PricingPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model=PricingPlan
        fields=['id','name','slug','monthly_price','annual_price','max_computations','storage_gb','max_api_calls','max_grid_size','support_level','features','created_at']
        read_only_fields=['id','created_at']
