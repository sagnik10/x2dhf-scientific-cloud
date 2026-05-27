# X2DHF-SaaS - Production Grade Django + React Application

## Overview
X2DHF-SaaS is a full-scale, production-ready SaaS platform for quantum chemistry computations supporting Hartree-Fock (HF), Density Functional Theory (DFT), and Quantum Espresso (QE) calculations.

## Architecture

### Backend (Django)
- **Framework**: Django 4.x with Django REST Framework
- **Authentication**: JWT (SimpleJWT) with Djoser
- **Database**: PostgreSQL with optimized indexes
- **Task Queue**: Celery + Redis
- **API**: RESTful with comprehensive serializers
- **Admin**: Full-featured Django Admin with customized interfaces

### Frontend (React)
- **Framework**: React 18.x with React Router v6
- **State Management**: Local state + API integration
- **Styling**: CSS3 with modern gradients and animations
- **Components**: Modular, reusable React components
- **API Client**: Axios with JWT token handling

## Key Features

### 1. **Computation Management**
- Create HF, DFT, and QE computations via user-friendly forms
- Real-time computation status tracking
- Automatic retry on failure
- Detailed execution logs and error messages
- Results download in JSON format

### 2. **User Management**
- JWT-based authentication
- Email verification
- User profiles with usage tracking
- Role-based access control (User/Admin)

### 3. **Admin Dashboard**
- Real-time statistics and analytics
- User management interface
- Computation monitoring
- System health checks
- Theory distribution charts

### 4. **Billing Integration**
- Stripe payment integration
- Usage tracking (API calls, storage, GPU hours)
- Invoice generation
- Payment history
- Pricing plans configuration

## Installation

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Redis 6+
- Docker & Docker Compose (optional)

### Local Development Setup

#### Backend
```bash
cd web/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

#### Frontend
```bash
cd web/frontend
npm install
npm start
```

### Docker Deployment
```bash
docker-compose -f docker-compose.prod.updated.yml up -d
```

## API Endpoints

### Computations
- `GET /api/computations/` - List user's computations
- `POST /api/computations/` - Create new computation
- `GET /api/computations/{id}/` - Get computation details
- `POST /api/computations/{id}/cancel/` - Cancel computation
- `POST /api/computations/{id}/retry/` - Retry failed computation

### Molecular Systems
- `GET /api/molecular-systems/` - List systems
- `POST /api/molecular-systems/` - Create system
- `DELETE /api/molecular-systems/{id}/` - Delete system

### Admin
- `GET /api/admin/statistics/` - Get system statistics
- `GET /api/admin/users/` - List all users
- `GET /api/admin/computations/{id}/` - Get computation details

## Environment Variables

### Backend (.env)
```
DEBUG=False
DJANGO_SECRET_KEY=your-secret-key
DB_NAME=x2dhf
DB_USER=postgres
DB_PASSWORD=secure-password
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
STRIPE_SECRET_KEY=sk_...
STRIPE_PUBLIC_KEY=pk_...
X2DHF_PATH=/usr/local/bin/x2dhf
X2DHF_DFT_PATH=/usr/local/bin/x2dhf_dft
QE_PATH=/usr/local/bin/pw.x
```

### Frontend (.env)
```
REACT_APP_API_URL=https://api.x2dhf.io
REACT_APP_WSS_URL=wss://api.x2dhf.io/ws
```

## Database Schema

### Key Models
- **User**: Extended Django user
- **Computation**: Stores computation metadata and results
- **ComputationParameter**: SCF parameters
- **ComputationLog**: Execution logs
- **MolecularSystem**: Molecular geometry data
- **Invoice**: Billing invoices
- **Payment**: Payment records
- **Usage**: User usage metrics

## Computation Flow

1. User creates computation via form
2. Form data saved to database
3. Computation queued in Celery
4. Worker executes calculation
5. Results stored in database
6. Frontend auto-refreshes status
7. Results displayable/downloadable

## Security

- JWT token-based authentication
- CORS restricted to allowed origins
- SQL injection protection via ORM
- CSRF protection on forms
- Password validation and hashing
- Rate limiting on API endpoints
- Secure headers (HSTS, CSP, etc.)

## Performance Optimizations

- Database indexes on frequently queried fields
- Lazy loading of computation logs
- Pagination on list endpoints
- Redis caching for admin statistics
- Static file compression
- Database connection pooling
- Celery task queue for async processing

## Monitoring & Logging

- Structured logging to console/file
- Django debug toolbar in development
- Sentry integration (optional)
- Application metrics (response times, error rates)
- Database query monitoring

## Testing

```bash
# Run backend tests
python manage.py test

# Run frontend tests
npm test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## Deployment

### Production Checklist
- [ ] Set DEBUG=False
- [ ] Configure allowed hosts
- [ ] Set secure SECRET_KEY
- [ ] Configure database backups
- [ ] Setup SSL certificates
- [ ] Configure email settings
- [ ] Setup monitoring/alerting
- [ ] Configure log aggregation
- [ ] Setup CDN for static files
- [ ] Configure database replicas

### Scaling
- Horizontal scaling: Multiple Gunicorn/Celery workers
- Database: Read replicas, sharding
- Caching: Redis clusters
- Load balancing: Nginx/HAProxy
- CDN: CloudFlare/AWS CloudFront

## Troubleshooting

### Computations Failing
1. Check computation logs in admin
2. Verify X2DHF/QE installation
3. Check disk space and memory
4. Review convergence thresholds
5. Check environment variables

### API Issues
1. Verify JWT token expiry
2. Check CORS settings
3. Review API rate limits
4. Check database connectivity

### Frontend Issues
1. Clear browser cache
2. Check API URL configuration
3. Verify authentication token
4. Check browser console for errors

## Support & Contributing

For issues, feature requests, or contributions, please visit the GitHub repository.

## License

Licensed under the X2DHF License. See LICENSE file for details.

---

**Last Updated**: 2026-05-26
**Version**: 1.0.0
