#!/bin/bash
set -e
echo "Building and starting X2DHF SaaS..."
docker-compose -f docker-compose.prod.yml up -d
echo "Waiting for services to be healthy..."
sleep 10
echo "Running migrations..."
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py migrate
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput
echo "Creating superuser..."
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py createsuperuser --noinput --username admin --email admin@example.com 2>/dev/null || true
echo "X2DHF SaaS is running!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Admin: http://localhost:8000/admin"
