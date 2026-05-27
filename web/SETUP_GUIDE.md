# X2DHF-SaaS Complete Setup Guide

## Project Structure

```
web/
├── backend/
│   ├── x2dhf_project/          # Django project
│   │   ├── settings.py         # Settings
│   │   ├── settings_prod.py    # Production settings
│   │   ├── urls.py             # URL routing
│   │   └── wsgi.py             # WSGI app
│   ├── computations/           # Computation app
│   │   ├── models.py           # Models (Computation, MolecularSystem, etc)
│   │   ├── views.py            # DRF ViewSets
│   │   ├── serializers.py      # DRF Serializers
│   │   ├── admin.py            # Django admin
│   │   ├── runner.py           # Computation runner logic
│   │   └── forms.py            # Django forms
│   ├── billing/                # Billing app
│   │   └── models.py           # Invoice, Payment models
│   ├── admin_api/              # Admin API endpoints
│   │   └── views.py            # Admin statistics & user mgmt
│   ├── users/                  # User authentication
│   ├── results/                # Results handling
│   ├── core/                   # Core functionality
│   ├── manage.py               # Django CLI
│   └── requirements.txt        # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main React component
│   │   ├── App.css             # Main styles
│   │   ├── components/
│   │   │   ├── ComputationsList.jsx        # List computations
│   │   │   ├── ComputationDetail.jsx       # View details
│   │   │   ├── HFComputationForm.jsx       # HF form
│   │   │   ├── DFTComputationForm.jsx      # DFT form
│   │   │   ├── QuantumEspressoForm.jsx     # QE form
│   │   │   ├── AdminDashboard.jsx          # Admin panel
│   │   │   ├── Computations.css            # List styles
│   │   │   ├── ComputationDetail.css       # Detail styles
│   │   │   ├── ComputationForm.css         # Form styles
│   │   │   └── AdminDashboard.css          # Admin styles
│   │   └── index.jsx           # React entry point
│   ├── package.json            # Node dependencies
│   └── Dockerfile
│
├── docker-compose.yml          # Dev docker compose
├── docker-compose.prod.updated.yml # Prod docker compose
├── nginx.updated.conf          # Nginx config
├── deploy.sh                   # Deployment script
└── README_DEPLOYMENT.md        # Full documentation
```

## Quick Start

### 1. Clone and Setup

```bash
git clone <repo-url>
cd x2dhf-main/web
```

### 2. Environment Setup

Create `.env` files:

**backend/.env**
```
DEBUG=True
DJANGO_SECRET_KEY=dev-secret-key-change-in-production
DB_NAME=x2dhf
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGINS=http://localhost:3000
```

**frontend/.env**
```
REACT_APP_API_URL=http://localhost:8000/api
```

### 3. Database Setup

```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run Services

**Terminal 1 - Backend**
```bash
cd backend
python manage.py runserver
```

**Terminal 2 - Frontend**
```bash
cd frontend
npm install
npm start
```

**Terminal 3 - Celery (optional for async)**
```bash
cd backend
celery -A x2dhf_project worker -l info
```

### 5. Access Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/
- API Docs: http://localhost:8000/api/docs/ (if configured)

## Database Models

### Computations App
- **Computation**: Main model storing computation metadata
- **MolecularSystem**: Molecular geometry and parameters
- **ComputationParameter**: SCF and theory-specific parameters
- **ComputationLog**: Execution logs for debugging

### Billing App
- **Invoice**: Billing invoices
- **Payment**: Payment transactions
- **Usage**: Monthly usage metrics
- **PricingPlan**: Subscription plan definitions
- **LineItem**: Invoice line items

### Users App (extends Django User)
- Custom authentication
- User profiles
- API token management

## Key Fixes Implemented

### 1. Decimal Field Fix (Line 10 - billing/models.py)
```python
# BEFORE (WRONG):
amount_paid=models.DecimalField(max_digits=10,decimal_places=2,default=0)

# AFTER (CORRECT):
from decimal import Decimal
amount_paid=models.DecimalField(max_digits=10,decimal_places=2,default=Decimal('0.00'))
```

### 2. ComputationLog Integration
Added ComputationLog model to track execution steps

### 3. Computation Runner
Full-featured runner supporting:
- Hartree-Fock (HF) calculations
- DFT with multiple functionals (LDA, GGA, Hybrid)
- Quantum Espresso calculations
- Error handling and timeouts
- Automatic logging

### 4. Admin Dashboard
- Real-time statistics
- User management
- Computation monitoring
- System health checks

### 5. Forms-Based Input System
- Dynamic form generation
- Parameter validation
- Real-time parameter adjustment
- Molecular system selection

## Computation Execution Flow

```
User Creates Form → Save to Database → Celery Queue → Runner Executes → 
Results Stored → Frontend Refreshes → User Sees Results
```

## Security Features

1. **Authentication**: JWT tokens with refresh mechanism
2. **Authorization**: Role-based access (User/Admin)
3. **API Security**: CORS restricted, rate limiting ready
4. **Database**: Parameterized queries prevent SQL injection
5. **Password**: Django's password hashers and validators
6. **Secrets**: Environment variables for sensitive data

## Performance Optimizations

1. **Database**: 
   - Indexes on frequent query fields
   - Connection pooling

2. **Frontend**:
   - Code splitting
   - Lazy loading components
   - API response caching

3. **Backend**:
   - Pagination (20 items/page)
   - Query optimization
   - Celery async tasks

4. **Infrastructure**:
   - Nginx reverse proxy
   - Static file compression
   - Redis caching

## Monitoring & Logs

Access logs in Docker:
```bash
docker logs <container-name>
docker logs -f <container-name>  # Follow logs
```

View computation logs in admin:
1. Go to http://localhost:8000/admin/
2. Navigate to "Computation Logs"
3. Filter by computation

## Troubleshooting

### Issue: Computations always fail
**Solution**: Check computation runner logs in admin

### Issue: JWT token expired
**Solution**: Frontend auto-refreshes tokens, check Redis availability

### Issue: Database connection error
**Solution**: Verify PostgreSQL running and .env variables correct

### Issue: Cors errors in frontend
**Solution**: Check CORS_ORIGINS in settings matches frontend URL

## Production Deployment

### Using Docker Compose (Recommended)
```bash
docker-compose -f docker-compose.prod.updated.yml up -d
```

### Manual Deployment
1. Install system dependencies:
   ```bash
   apt-get install python3 postgresql redis-server nginx
   ```

2. Install Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Setup database:
   ```bash
   python manage.py migrate
   python manage.py collectstatic
   ```

4. Run with Gunicorn:
   ```bash
   gunicorn x2dhf_project.wsgi:application --bind 0.0.0.0:8000 --workers 4
   ```

5. Configure Nginx reverse proxy

6. Setup SSL certificates (Let's Encrypt recommended)

## Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test computations

# With coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Scaling for Production

### Horizontal Scaling
- Run multiple Gunicorn workers
- Run multiple Celery workers
- Use database read replicas

### Vertical Scaling
- Increase server RAM
- More CPU cores
- SSD storage

### Infrastructure
- CDN for static files
- Database clusters
- Redis cluster
- Kubernetes for orchestration

## Support

For issues or questions:
1. Check logs in admin panel
2. Review computation error messages
3. Verify environment variables
4. Check database connectivity

---

**Version**: 1.0.0
**Last Updated**: 2026-05-26
**Status**: Production Ready ✅
