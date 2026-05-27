from django.conf import settings
from django.db import migrations
from django.utils import timezone

def create_missing_usage(apps,schema_editor):
    User=apps.get_model('auth','User')
    Usage=apps.get_model('billing','Usage')
    reset_date=timezone.now().date()
    for user in User.objects.all():
        Usage.objects.get_or_create(user=user,defaults={'reset_date':reset_date})

class Migration(migrations.Migration):
    dependencies=[('billing','0001_initial'),migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations=[
        migrations.AlterModelOptions(name='invoice',options={'ordering':['-created_at']}),
        migrations.AlterModelOptions(name='payment',options={'ordering':['-created_at']}),
        migrations.AlterModelOptions(name='pricingplan',options={'ordering':['monthly_price','id']}),
        migrations.RunPython(create_missing_usage,migrations.RunPython.noop),
    ]
