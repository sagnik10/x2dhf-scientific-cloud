#!/bin/bash
set -e
echo "=== X2DHF-SaaS Deployment Script ===="
echo "Installing dependencies..."
pip install django djangorestframework djangorestframework-simplejwt djoser django-cors-headers django-filter psycopg2-binary stripe celery redis gunicorn whitenoise
echo "Running migrations..."
python manage.py migrate
echo "Creating superuser..."
python manage.py createsuperuser --noinput --username admin --email admin@x2dhf.io 2>/dev/null || true
echo "Collecting static files..."
python manage.py collectstatic --noinput
echo "=== Deployment Complete ==="
