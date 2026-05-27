from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
class Invoice(models.Model):
    STATUS_CHOICES=[('draft','Draft'),('sent','Sent'),('paid','Paid'),('overdue','Overdue'),('cancelled','Cancelled'),]
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='invoices')
    stripe_id=models.CharField(max_length=255,blank=True)
    invoice_number=models.CharField(max_length=50,unique=True)
    status=models.CharField(max_length=50,choices=STATUS_CHOICES,default='draft')
    amount_due=models.DecimalField(max_digits=10,decimal_places=2)
    amount_paid=models.DecimalField(max_digits=10,decimal_places=2,default=Decimal('0.00'))
    currency=models.CharField(max_length=3,default='USD')
    issue_date=models.DateField(auto_now_add=True)
    due_date=models.DateField()
    paid_date=models.DateField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        db_table='invoices'
        ordering=['-created_at']
        indexes=[models.Index(fields=['user','-created_at']),]
class LineItem(models.Model):
    invoice=models.ForeignKey(Invoice,on_delete=models.CASCADE,related_name='items')
    description=models.CharField(max_length=255)
    quantity=models.IntegerField()
    unit_price=models.DecimalField(max_digits=10,decimal_places=2)
    total=models.DecimalField(max_digits=10,decimal_places=2)
    class Meta:
        db_table='line_items'
class Usage(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='usage')
    computations_this_month=models.IntegerField(default=0)
    storage_used_gb=models.FloatField(default=0)
    api_calls_this_month=models.IntegerField(default=0)
    gpu_hours_this_month=models.FloatField(default=0)
    reset_date=models.DateField()
    class Meta:
        db_table='usage'
class PricingPlan(models.Model):
    name=models.CharField(max_length=100,unique=True)
    slug=models.SlugField(unique=True)
    monthly_price=models.DecimalField(max_digits=10,decimal_places=2)
    annual_price=models.DecimalField(max_digits=10,decimal_places=2)
    max_computations=models.IntegerField()
    storage_gb=models.IntegerField()
    max_api_calls=models.IntegerField()
    max_grid_size=models.IntegerField()
    support_level=models.CharField(max_length=50,choices=[('community','Community'),('standard','Standard'),('priority','Priority')])
    features=models.JSONField(default=list)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table='pricing_plans'
        ordering=['monthly_price','id']
class Payment(models.Model):
    STATUS_CHOICES=[('pending','Pending'),('completed','Completed'),('failed','Failed'),('refunded','Refunded'),]
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='payments')
    invoice=models.ForeignKey(Invoice,on_delete=models.SET_NULL,null=True,blank=True)
    stripe_payment_id=models.CharField(max_length=255,unique=True)
    amount=models.DecimalField(max_digits=10,decimal_places=2)
    currency=models.CharField(max_length=3,default='USD')
    status=models.CharField(max_length=50,choices=STATUS_CHOICES,default='pending')
    payment_method=models.CharField(max_length=50,choices=[('card','Card'),('bank','Bank Transfer'),('paypal','PayPal')])
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        db_table='payments'
        ordering=['-created_at']
        indexes=[models.Index(fields=['user','-created_at']),]
