from django.db import migrations,models
import users.models

def fill_api_keys(apps,schema_editor):
    UserProfile=apps.get_model('users','UserProfile')
    for profile in UserProfile.objects.filter(api_key=''):
        profile.api_key=users.models.generate_api_key()
        profile.save(update_fields=['api_key'])

class Migration(migrations.Migration):
    dependencies=[('users','0001_initial')]
    operations=[
        migrations.AlterField(
            model_name='userprofile',
            name='api_key',
            field=models.CharField(blank=True,default=users.models.generate_api_key,max_length=255,unique=True),
        ),
        migrations.RunPython(fill_api_keys,migrations.RunPython.noop),
    ]
