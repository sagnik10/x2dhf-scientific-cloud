# X2DHF-SaaS Quick Reference Guide

## 🚀 Quick Start (5 minutes)

### 1. Clone Repository
```bash
git clone <repo-url>
cd x2dhf-main/web
```

### 2. Setup Environment
```bash
# Backend
cd backend
cp .env.example .env
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### 3. Database
```bash
cd ../backend
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run Application
```bash
# Terminal 1: Backend
cd backend && python manage.py runserver

# Terminal 2: Frontend
cd frontend && npm start

# Terminal 3: Celery (optional)
cd backend && celery -A x2dhf_project worker -l info
```

### 5. Access
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Admin: http://localhost:8000/admin

---

## 📁 Project Structure Quick Reference

```
backend/
  ├── computations/    → Computation models & logic
  ├── billing/         → Billing models & payments
  ├── users/           → Authentication
  ├── admin_api/       → Admin endpoints
  ├── manage.py        → Django CLI
  └── requirements.txt → Python packages

frontend/
  ├── src/
  │   ├── components/  → React components
  │   ├── App.jsx      → Main app
  │   └── App.css      → Styles
  └── package.json     → NPM packages
```

---

## 🔑 Key API Endpoints

### Computations
- `GET /api/computations/` - List all
- `POST /api/computations/` - Create
- `GET /api/computations/{id}/` - Details
- `POST /api/computations/{id}/cancel/` - Cancel
- `POST /api/computations/{id}/retry/` - Retry

### Molecular Systems
- `GET /api/molecular-systems/` - List
- `POST /api/molecular-systems/` - Create
- `DELETE /api/molecular-systems/{id}/` - Delete

### Admin
- `GET /api/admin/statistics/` - Stats
- `GET /api/admin/users/` - Users
- `POST /api/admin/computations/{id}/retry/` - Retry

---

## 💾 Database Models Cheat Sheet

### Computation
```python
Computation(
    title,              # Computation name
    theory,             # 'hf', 'dft', 'qe'
    status,             # 'pending', 'running', 'completed', 'failed'
    output_data,        # JSON results
    error_message,      # Error details
    cpu_time_seconds,   # Execution time
)
```

### MolecularSystem
```python
MolecularSystem(
    name,               # System name
    molecule_formula,   # e.g., 'H2O'
    geometry_type,      # 'atom', 'diatomic', 'linear'
    grid_size_x,        # Grid points X
    grid_size_y,        # Grid points Y
)
```

### ComputationLog
```python
ComputationLog(
    computation,        # Foreign key
    level,             # 'INFO', 'WARNING', 'ERROR'
    message,           # Log message
)
```

---

## 🎨 Component Props Reference

### ComputationsList
- Filters by status and theory
- Lists all user computations
- Real-time status

### ComputationDetail
- Shows full computation info
- Auto-refreshes status
- Download results
- View logs

### HFComputationForm
- Title, description
- Molecular system selection
- SCF iterations, convergence threshold
- Spin multiplicity, num electrons

### DFTComputationForm
- + Functional selection (LDA/GGA/Hybrid)
- Extended parameter set

### QuantumEspressoForm
- + K-points grid
- + Ecutwfc/ecutrho
- + Pseudopotential

### AdminDashboard
- Real-time stats
- User management
- Computation monitoring

---

## 🔐 Authentication

### Login
```javascript
POST /api/auth/jwt/create/
{
    "email": "user@example.com",
    "password": "password123"
}
// Returns: { "access": "token", "refresh": "token" }
```

### API Requests
```javascript
const headers = {
    'Authorization': `Bearer ${localStorage.getItem('token')}`
};
axios.get('/api/computations/', { headers });
```

### Token Refresh
```javascript
POST /api/auth/jwt/refresh/
{ "refresh": "refresh_token" }
```

---

## 🐛 Debugging Tips

### Backend Logs
```bash
# View Django logs
python manage.py runserver  # Shows errors

# Check Celery
celery -A x2dhf_project worker -l debug

# Database queries
# Add to settings.py:
LOGGING = {'version': 1, ...}
```

### Frontend Logs
```bash
# Console logs
console.log(), console.error()

# Network tab in DevTools
# Check API responses and errors

# React DevTools
# Inspect component state
```

### Computation Issues
1. Check admin panel "Computation Logs"
2. View error_message field
3. Check runner output in Celery logs
4. Verify environment variables

---

## 🚀 Deployment Checklist

- [ ] Set `DEBUG=False`
- [ ] Change `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Setup PostgreSQL
- [ ] Setup Redis
- [ ] Configure SSL/TLS
- [ ] Setup email backend
- [ ] Configure Stripe keys
- [ ] Setup backups
- [ ] Enable monitoring
- [ ] Load test
- [ ] Security audit

---

## 📊 Performance Tips

1. **Backend**
   - Use database indexes ✅
   - Pagination enabled ✅
   - Query optimization ✅
   - Redis caching ready ✅

2. **Frontend**
   - Code splitting ready
   - Lazy load components
   - Minimize API calls
   - Use React.memo

3. **Infrastructure**
   - Nginx reverse proxy ✅
   - Gunicorn workers ✅
   - Static compression ✅
   - CDN ready ✅

---

## 🔧 Common Commands

```bash
# Backend
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
python manage.py shell
python manage.py test

# Frontend
npm start           # Dev server
npm build          # Production build
npm test           # Run tests
npm install [pkg]  # Install package

# Docker
docker-compose up -d
docker-compose down
docker-compose logs -f [service]
docker-compose exec [service] [command]

# Git
git add .
git commit -m "message"
git push origin main
git pull origin main
```

---

## 📞 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 in use | `lsof -i :8000` then kill process |
| Port 3000 in use | `lsof -i :3000` then kill process |
| Database error | Ensure PostgreSQL running, check .env |
| CORS error | Check CORS_ORIGINS in settings |
| JWT expired | Frontend auto-refreshes, check Redis |
| Computation failed | Check admin logs, verify runner setup |
| Static files 404 | Run `collectstatic`, check STATIC_URL |
| NPM modules error | Delete node_modules, run `npm install` |

---

## 📚 Useful Resources

- Django Docs: https://docs.djangoproject.com
- DRF: https://www.django-rest-framework.org
- React: https://react.dev
- PostgreSQL: https://www.postgresql.org/docs
- Docker: https://docs.docker.com

---

## 🎯 Next Steps

1. ✅ Setup complete
2. ✅ Run locally
3. ✅ Test all features
4. ✅ Deploy to staging
5. ✅ Run security audit
6. ✅ Deploy to production
7. ✅ Setup monitoring
8. ✅ Configure backups

---

**Last Updated**: May 26, 2026
**Version**: 1.0.0
