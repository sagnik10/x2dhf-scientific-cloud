# Environment Variables Template

## Backend (.env)

```
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-key-change-this-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=x2dhf
DB_USER=postgres
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=

# JWT Settings
JWT_SECRET=your-jwt-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_LIFETIME=86400
JWT_REFRESH_TOKEN_LIFETIME=604800

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:8000,https://yourdomain.com

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@x2dhf.io

# Stripe Payments
STRIPE_SECRET_KEY=sk_test_your_secret_key
STRIPE_PUBLIC_KEY=pk_test_your_public_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# External Tools Paths
X2DHF_PATH=/usr/local/bin/x2dhf
X2DHF_DFT_PATH=/usr/local/bin/x2dhf_dft
QE_PATH=/usr/local/bin/pw.x
LIBXC_PATH=/usr/local/lib

# Computation Settings
AUTO_START_COMPUTATIONS=False
COMPUTATION_TIMEOUT_HF=600
COMPUTATION_TIMEOUT_DFT=600
COMPUTATION_TIMEOUT_QE=1200
MAX_PARALLEL_COMPUTATIONS=10

# AWS S3 (Optional)
USE_S3=False
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=us-east-1

# Sentry Error Tracking (Optional)
SENTRY_DSN=

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/x2dhf/django.log

# Application
TIMEZONE=UTC
LANGUAGE_CODE=en-us
```

## Frontend (.env)

```
# API Configuration
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_API_TIMEOUT=30000

# WebSocket Configuration
REACT_APP_WSS_URL=ws://localhost:8000/ws
REACT_APP_WSS_RECONNECT_INTERVAL=5000

# Stripe Configuration
REACT_APP_STRIPE_PUBLIC_KEY=pk_test_your_public_key

# Application Settings
REACT_APP_APP_NAME=X2DHF-SaaS
REACT_APP_VERSION=1.0.0
REACT_APP_LOG_LEVEL=error

# Feature Flags
REACT_APP_ENABLE_ADMIN=true
REACT_APP_ENABLE_BILLING=true
REACT_APP_ENABLE_DARK_MODE=false

# Analytics (Optional)
REACT_APP_GOOGLE_ANALYTICS_ID=
REACT_APP_MIXPANEL_TOKEN=

# Support
REACT_APP_SUPPORT_EMAIL=support@x2dhf.io
REACT_APP_DOCS_URL=https://docs.x2dhf.io
```

## Docker Environment (.env)

```
# Compose Settings
COMPOSE_PROJECT_NAME=x2dhf
COMPOSE_FILE=docker-compose.prod.updated.yml

# Service Configuration
POSTGRES_DB=x2dhf
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123

REDIS_PASSWORD=

# Backend Settings (inherited from above)
DEBUG=False
DJANGO_SECRET_KEY=docker-secret-key

# Network
BACKEND_PORT=8000
FRONTEND_PORT=3000
NGINX_PORT=80
NGINX_PORT_HTTPS=443

# Volumes
POSTGRES_DATA_VOLUME=/var/lib/postgresql/data
REDIS_DATA_VOLUME=/data
STATIC_FILES_VOLUME=/app/staticfiles
MEDIA_FILES_VOLUME=/app/media
```

## Development Settings (.env.development)

```
# Django
DEBUG=True
SECRET_KEY=dev-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Using SQLite for development)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# No Redis needed in development
USE_CACHE=False

# Stripe Test Keys
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLIC_KEY=pk_test_xxx

# Email to Console
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Auto-start computations
AUTO_START_COMPUTATIONS=True

# Frontend
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_API_TIMEOUT=30000
DEBUG=true
```

## Production Settings (.env.production)

```
# Django
DEBUG=False
SECRET_KEY=your-production-secret-key-at-least-50-chars
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,api.yourdomain.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=x2dhf_prod
DB_USER=x2dhf_user
DB_PASSWORD=your-very-secure-password
DB_HOST=db.yourdomain.com
DB_PORT=5432

# Redis
REDIS_URL=redis://redis.yourdomain.com:6379/0
REDIS_PASSWORD=your-redis-password

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key

# Stripe Production Keys
STRIPE_SECRET_KEY=sk_live_your_secret_key
STRIPE_PUBLIC_KEY=pk_live_your_public_key

# External Tools
X2DHF_PATH=/opt/x2dhf/bin/x2dhf
X2DHF_DFT_PATH=/opt/x2dhf/bin/x2dhf_dft
QE_PATH=/opt/quantum-espresso/bin/pw.x

# Logging
LOG_LEVEL=WARNING
LOG_FILE=/var/log/x2dhf/django.log

# Frontend
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_STRIPE_PUBLIC_KEY=pk_live_your_public_key

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# Database Backups
BACKUP_ENABLED=True
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION_DAYS=30
```

## Testing Settings (.env.test)

```
DEBUG=True
SECRET_KEY=test-secret-key
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=:memory:
USE_CACHE=False
EMAIL_BACKEND=django.core.mail.backends.locmem.EmailBackend
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLIC_KEY=pk_test_xxx
AUTO_START_COMPUTATIONS=False
```

---

## Setup Instructions

### 1. Copy Template to .env
```bash
# Backend
cd backend
cp .env.example .env  # or use environment-specific
nano .env  # Edit with your values

# Frontend
cd ../frontend
cp .env.example .env
nano .env  # Edit with your values
```

### 2. Create .env Files
```bash
# Development
cp .env.development .env

# Production
cp .env.production .env

# Testing
cp .env.test .env
```

### 3. Secure Sensitive Data
- Never commit .env files to git
- Use .env.example for template
- Rotate keys regularly in production
- Use secrets manager (e.g., HashiCorp Vault)

### 4. Docker Secrets (for production)
```bash
# Create Docker secrets
docker secret create django_secret_key -
docker secret create db_password -
docker secret create stripe_secret -
```

---

## Important Notes

⚠️ **Security**
- Change SECRET_KEY immediately in production
- Use strong, random passwords (40+ characters)
- Never expose .env files publicly
- Rotate API keys regularly
- Use HTTPS only in production

⚠️ **Configuration**
- Update ALLOWED_HOSTS for your domain
- Configure CORS_ORIGINS properly
- Set correct database credentials
- Verify tool paths (X2DHF, QE)

⚠️ **Email**
- Test email setup before going live
- Use SendGrid/AWS SES for production
- Configure sender address properly

⚠️ **Payments**
- Always use production Stripe keys in prod
- Keep webhook secrets secure
- Test payment flow thoroughly

---

**Last Updated**: May 26, 2026
**Version**: 1.0.0
