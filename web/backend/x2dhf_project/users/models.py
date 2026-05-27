from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator,MinValueValidator
from secrets import token_urlsafe

def generate_api_key():
    return token_urlsafe(32)

class UserProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    organization=models.CharField(max_length=255,blank=True)
    api_key=models.CharField(max_length=255,unique=True,blank=True,default=generate_api_key)
    storage_used_gb=models.FloatField(default=0)
    monthly_computations=models.IntegerField(default=0)
    plan=models.CharField(max_length=50,choices=[('free','Free'),('pro','Pro'),('enterprise','Enterprise')],default='free')
    subscription_active=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        db_table='user_profiles'
class Subscription(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='subscription')
    plan=models.CharField(max_length=50,choices=[('free','Free'),('pro','Pro'),('enterprise','Enterprise')])
    stripe_id=models.CharField(max_length=255,blank=True)
    status=models.CharField(max_length=50,choices=[('active','Active'),('paused','Paused'),('cancelled','Cancelled')],default='active')
    current_period_start=models.DateTimeField()
    current_period_end=models.DateTimeField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        db_table='subscriptions'
class APIAuditLog(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    endpoint=models.CharField(max_length=255)
    method=models.CharField(max_length=10)
    status_code=models.IntegerField()
    ip_address=models.GenericIPAddressField()
    timestamp=models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table='api_audit_logs'
        indexes=[models.Index(fields=['user','timestamp']),]
