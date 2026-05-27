from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile,Subscription
from billing.models import Usage
from datetime import timedelta
from django.utils import timezone
@receiver(post_save,sender=User)
def create_user_profile(sender,instance,created,**kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        now=timezone.now()
        Subscription.objects.create(user=instance,plan='free',current_period_start=now,current_period_end=now+timedelta(days=30))
        Usage.objects.create(user=instance,reset_date=now.date())
@receiver(post_save,sender=User)
def save_user_profile(sender,instance,**kwargs):
    instance.profile.save()
    
