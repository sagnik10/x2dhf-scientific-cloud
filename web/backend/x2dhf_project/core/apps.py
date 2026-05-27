import os
from django.apps import AppConfig
from django.conf import settings

class CoreConfig(AppConfig):
    default_auto_field='django.db.models.BigAutoField'
    name='core'

    def ready(self):
        if os.environ.get('RUN_MAIN')!='true' or os.environ.get('X2DHF_SKIP_DEV_ADMIN'):
            return
        if not settings.DEBUG or os.environ.get('X2DHF_CREATE_DEV_ADMIN')!='1':
            return
        try:
            from django.contrib.auth.models import User
            from django.db import connection
            if 'auth_user' not in connection.introspection.table_names():
                return
            email=os.environ.get('X2DHF_ADMIN_EMAIL')
            password=os.environ.get('X2DHF_ADMIN_PASSWORD')
            if not email or not password:
                return
            user,created=User.objects.get_or_create(username='admin',defaults={'email':email,'is_staff':True,'is_superuser':True})
            changed=created or not user.is_staff or not user.is_superuser or user.email!=email
            user.email=email
            user.is_staff=True
            user.is_superuser=True
            user.is_active=True
            if created or not user.has_usable_password():
                user.set_password(password)
                changed=True
            if changed:
                user.save()
        except Exception:
            return
