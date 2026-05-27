import os
from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE','x2dhf_project.settings')
app=Celery('x2dhf_project')
app.config_from_object('django.conf:settings',namespace='CELERY')
app.autodiscover_tasks()
