# X2DHF SaaS Platform

Full-stack production-grade SaaS application for X2DHF quantum chemistry calculations.

## Features

- **User Management**: JWT authentication, profiles, API keys
- **Molecular Systems**: Create and manage molecular geometries
- **Computations**: Hartree-Fock and DFT calculations with async processing
- **Results Management**: Compute results with visualization and export
- **Billing**: Stripe integration, usage tracking, subscription management
- **API**: RESTful API with comprehensive documentation
- **Frontend**: React SPA with Redux state management
- **DevOps**: Docker, docker-compose, nginx, CI/CD ready

## Architecture

### Backend (Django)
- REST API with DRF
- Async task processing with Celery
- PostgreSQL database
- Redis caching and message broker
- Stripe payment integration
- JWT authentication

### Frontend (React)
- Redux state management
- React Router for navigation
- Axios for API calls
- Tailwind CSS styling
- React Query for data fetching

### Infrastructure
- Docker containerization
- Nginx reverse proxy
- PostgreSQL 15
- Redis 7
- Gunicorn WSGI server
- GitHub Actions CI/CD

## Installation

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)

### Development Setup

```bash
git clone https://github.com/yourusername/x2dhf-saas.git
cd x2dhf-saas
cp .env.example .env
docker-compose up -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

Access:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Admin: http://localhost:8000/admin

### Production Deployment

```bash
docker-compose -f docker-compose.prod.yml up -d
bash scripts/start.sh
```

## API Documentation

### Authentication
- POST `/api/auth/jwt/create/` - Login
- POST `/api/auth/users/` - Register
- POST `/api/auth/jwt/refresh/` - Refresh token

### Users
- GET `/api/users/users/me/` - Get profile
- PATCH `/api/users/users/me/` - Update profile
- POST `/api/users/users/generate_api_key/` - Generate API key
- GET `/api/users/users/usage/` - Get usage stats

### Computations
- GET/POST `/api/computations/systems/` - Molecular systems
- GET/POST `/api/computations/jobs/` - Computation jobs
- POST `/api/computations/jobs/{id}/cancel/` - Cancel job
- POST `/api/computations/jobs/{id}/retry/` - Retry failed job
- GET `/api/computations/jobs/statistics/` - Job statistics

### Results
- GET `/api/results/results/` - List results
- GET `/api/results/results/{id}/` - Get result details
- POST `/api/results/results/{id}/export/` - Export result
- GET `/api/results/visualizations/` - List visualizations

### Billing
- GET `/api/billing/invoices/` - List invoices
- POST `/api/billing/invoices/{id}/pay/` - Pay invoice
- GET `/api/billing/payments/` - Payment history
- GET `/api/billing/usage/current/` - Current usage
- GET `/api/billing/pricing/` - Pricing plans
- POST `/api/users/subscriptions/upgrade/` - Upgrade plan

## Project Structure

```
x2dhf-saas/
├── backend/
│   ├── x2dhf_project/
│   │   ├── users/
│   │   ├── computations/
│   │   ├── results/
│   │   ├── billing/
│   │   ├── core/
│   │   └── settings.py
│   ├── tests/
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── store/
│   │   ├── api/
│   │   └── App.js
│   ├── public/
│   └── package.json
├── scripts/
│   ├── start.sh
│   ├── stop.sh
│   └── logs.sh
├── docker-compose.yml
├── docker-compose.prod.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── nginx.conf
└── .env.example
```

## Environment Variables

See `.env.example` for all configuration options:
- Database credentials
- Secret keys
- Stripe API keys
- Service URLs
- Feature flags

## Testing

```bash
cd backend
pytest
```

Frontend tests:
```bash
cd frontend
npm test
```

## CI/CD

GitHub Actions pipeline runs on every push:
- Python linting and tests
- Database migrations
- Frontend build

## Security

- JWT token authentication
- CORS configuration
- CSRF protection
- Password validation
- Rate limiting
- SQL injection prevention
- Secure headers

## Performance

- Database indexing
- Redis caching
- Async task processing
- Static file compression
- Nginx caching

## License

MIT License

## Support

Contact: support@x2dhf.com
