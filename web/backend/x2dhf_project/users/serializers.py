from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile,Subscription
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','username','email','first_name','last_name','date_joined']
        read_only_fields=['id','date_joined']
class UserProfileSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model=UserProfile
        fields=['id','user','organization','api_key','storage_used_gb','monthly_computations','plan','subscription_active','created_at','updated_at']
        read_only_fields=['id','api_key','storage_used_gb','created_at','updated_at']
class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Subscription
        fields=['id','user','plan','status','current_period_start','current_period_end','created_at','updated_at']
        read_only_fields=['id','stripe_id','created_at','updated_at']
class UserDetailSerializer(serializers.ModelSerializer):
    profile=UserProfileSerializer(read_only=True)
    subscription=SubscriptionSerializer(read_only=True)
    class Meta:
        model=User
        fields=['id','username','email','first_name','last_name','is_staff','is_superuser','profile','subscription','date_joined']
        read_only_fields=['id','date_joined']
