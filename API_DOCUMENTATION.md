# X2DHF-SaaS API Documentation

## Base URL
```
http://localhost:8000/api
https://api.yourdomain.com
```

## Authentication
All endpoints require JWT token in header:
```
Authorization: Bearer {access_token}
```

## Response Format
```json
{
  "count": 100,
  "next": "http://api/endpoint?page=2",
  "previous": null,
  "results": []
}
```

---

## Authentication Endpoints

### 1. Obtain Token
```
POST /auth/jwt/create/
```
**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```
**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 2. Refresh Token
```
POST /auth/jwt/refresh/
```
**Request:**
```json
{
  "refresh": "{refresh_token}"
}
```

### 3. Verify Token
```
POST /auth/jwt/verify/
```
**Request:**
```json
{
  "token": "{access_token}"
}
```

---

## Computations Endpoints

### 1. List Computations
```
GET /computations/
```
**Query Parameters:**
```
?status=completed      # Filter by status
?theory=hf            # Filter by theory
?page=1               # Pagination
```
**Response:**
```json
{
  "count": 42,
  "results": [
    {
      "id": 1,
      "title": "H Atom HF",
      "theory": "hf",
      "status": "completed",
      "created_at": "2026-05-26T10:30:00Z",
      "cpu_time_seconds": 45.23
    }
  ]
}
```

### 2. Create Computation
```
POST /computations/
```
**Request:**
```json
{
  "title": "Water HF Calculation",
  "description": "Hartree-Fock for water molecule",
  "molecular_system": 1,
  "theory": "hf",
  "spin_multiplicity": 1,
  "num_electrons": 10,
  "scf_iterations": 100,
  "convergence_threshold": 1e-6,
  "parameters": [
    {
      "key": "grid_size_r",
      "value": "500"
    }
  ]
}
```
**Response:** 201 Created
```json
{
  "id": 42,
  "title": "Water HF Calculation",
  "status": "pending",
  "created_at": "2026-05-26T10:35:00Z"
}
```

### 3. Get Computation Detail
```
GET /computations/{id}/
```
**Response:**
```json
{
  "id": 42,
  "title": "Water HF Calculation",
  "description": "Hartree-Fock for water molecule",
  "theory": "hf",
  "status": "completed",
  "output_data": {
    "total_energy": -76.1167,
    "homo_energy": -0.5,
    "lumo_energy": 0.2,
    "homo_lumo_gap": 0.7,
    "dipole_moment": 1.85
  },
  "cpu_time_seconds": 45.23,
  "logs": [
    {
      "level": "INFO",
      "message": "Starting Hartree-Fock calculation",
      "timestamp": "2026-05-26T10:35:00Z"
    }
  ]
}
```

### 4. Cancel Computation
```
POST /computations/{id}/cancel/
```
**Response:** 200 OK
```json
{
  "message": "Computation cancelled"
}
```

### 5. Retry Computation
```
POST /computations/{id}/retry/
```
**Response:** 200 OK
```json
{
  "message": "Computation retry started"
}
```

### 6. Computation Statistics
```
GET /computations/statistics/
```
**Response:**
```json
{
  "total": 100,
  "completed": 85,
  "failed": 5,
  "running": 3,
  "pending": 7,
  "cpu_time_seconds": 4523.45,
  "average_cpu_time_seconds": 45.23,
  "by_theory": [
    {"theory": "hf", "count": 50},
    {"theory": "dft", "count": 40},
    {"theory": "qe", "count": 10}
  ]
}
```

---

## Molecular Systems Endpoints

### 1. List Systems
```
GET /molecular-systems/
```
**Query Parameters:**
```
?geometry_type=atom
?symmetry=Cs
?page=1
```

### 2. Create System
```
POST /molecular-systems/
```
**Request:**
```json
{
  "name": "Water Molecule",
  "description": "H2O in Cs symmetry",
  "molecule_formula": "H2O",
  "geometry_type": "linear",
  "symmetry": "Cs",
  "grid_spacing": 0.1,
  "max_radius": 50.0,
  "grid_size_x": 200,
  "grid_size_y": 200
}
```

### 3. Get System Detail
```
GET /molecular-systems/{id}/
```

### 4. Update System
```
PUT /molecular-systems/{id}/
```

### 5. Delete System
```
DELETE /molecular-systems/{id}/
```

---

## Admin Endpoints (Superuser only)

### 1. System Statistics
```
GET /admin/statistics/
```
**Response:**
```json
{
  "total_computations": 1000,
  "completed_computations": 850,
  "failed_computations": 50,
  "running_computations": 5,
  "pending_computations": 95,
  "active_users": 127,
  "total_users": 245,
  "total_cpu_time_hours": 1250.5,
  "avg_execution_time_sec": 45.23,
  "theory_distribution": {
    "hf": 500,
    "dft": 400,
    "qe": 100
  }
}
```

### 2. List Users
```
GET /admin/users/
```
**Response:**
```json
[
  {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "date_joined": "2026-01-15",
    "last_login": "2026-05-26",
    "computation_count": 42
  }
]
```

### 3. Get Computation Details
```
GET /admin/computations/{id}/
```

### 4. Retry Computation (Admin)
```
POST /admin/computations/{id}/retry/
```

---

## Error Responses

### 400 Bad Request
```json
{
  "field_name": ["error message"],
  "non_field_errors": ["error message"]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Server Error |

---

## Computation Status Values

- `pending` - Waiting to start
- `running` - Currently executing
- `completed` - Finished successfully
- `failed` - Execution failed
- `cancelled` - User cancelled

---

## Theory Types

- `hf` - Hartree-Fock (X2DHF)
- `dft` - Density Functional Theory (X2DHF)
- `qe` - Quantum Espresso

---

## DFT Functionals

- `LDA` - Local Density Approximation
- `GGA` - Generalized Gradient Approximation
- `HYBRID` - Hybrid functionals

---

## Geometry Types

- `atom` - Single atom
- `diatomic` - Two atoms (HF, H2, etc)
- `linear` - Linear molecules (H2O, CO2)

---

## Symmetry Groups

- `C2v` - C2v symmetry
- `Cs` - Cs symmetry
- `C2` - C2 symmetry
- `Ci` - Ci symmetry
- `D_inf_h` - D∞h symmetry
- `C_inf_v` - C∞v symmetry

---

## Request/Response Examples

### Example 1: Create HF Computation
```bash
curl -X POST http://localhost:8000/api/computations/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "H Atom",
    "molecular_system": 1,
    "theory": "hf",
    "num_electrons": 1,
    "spin_multiplicity": 2,
    "scf_iterations": 100,
    "convergence_threshold": 1e-6
  }'
```

### Example 2: Get Computation Results
```bash
curl http://localhost:8000/api/computations/42/ \
  -H "Authorization: Bearer {token}"
```

### Example 3: Cancel Computation
```bash
curl -X POST http://localhost:8000/api/computations/42/cancel/ \
  -H "Authorization: Bearer {token}"
```

---

## Filtering & Search

### Computations Filtering
```
GET /computations/?status=completed
GET /computations/?theory=hf
GET /computations/?status=completed&theory=dft
```

### Search
```
GET /computations/?search=water
GET /molecular-systems/?search=H2O
```

### Ordering
```
GET /computations/?ordering=-created_at
GET /computations/?ordering=status
```

---

## Pagination

Default: 20 items per page

```
GET /computations/?page=1
GET /computations/?page=2
```

Response includes:
```json
{
  "count": 100,
  "next": "http://api/computations/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Rate Limiting
Currently no rate limiting. Configure in production:
```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

---

## CORS Headers
```
Access-Control-Allow-Origin: {allowed-origin}
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, PATCH
Access-Control-Allow-Headers: Content-Type, Authorization
```

---

## Content Types
- Request: `application/json`
- Response: `application/json`

---

## Webhook Events (for Stripe)
- `payment.succeeded`
- `payment.failed`
- `invoice.paid`
- `invoice.payment_failed`

---

## SDK & Client Libraries

### JavaScript/Node.js
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

api.get('/computations/').then(res => console.log(res.data));
```

### Python
```python
import requests

headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://localhost:8000/api/computations/', 
                       headers=headers)
print(response.json())
```

### cURL
See examples above

---

## Rate Limit Headers
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1234567890
```

---

**Version**: 1.0.0
**Last Updated**: May 26, 2026
