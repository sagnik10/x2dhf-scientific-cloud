# X2DHF Scientific Cloud

A modern **Python-first Django + React scientific cloud platform** for **X2DHF-style Hartree-Fock (HF) and Density Functional Theory (DFT) computations**, featuring guided scientific input generation, runtime execution, stored computation history, analytics dashboards, theory publishing, and configurable runtime workflows.

---

## 🎥 Prototype Demonstration

**Demo Video:**  
https://drive.google.com/file/d/1MWJwffOT-YflU_OGyWNLSmeCculdvHZf/view?usp=sharing

This prototype demonstrates the X2DHF Scientific Cloud interface, scientific workflow, runtime execution, computation management, dashboards, and guided HF/DFT computation environment.

---

## Features

- **Django 4 backend** with JWT authentication.
- **React frontend** integrated into Django.
- **Python-first scientific runtime** for:
  - Hartree-Fock (HF)
  - Density Functional Theory (DFT)
  - HFS
  - OED
  - TED
  - SCMC
  - Quantum Espresso-style scientific workflows
- **X2DHF-style guided input builder**:
  - Atoms and molecules
  - Grid cards
  - SCF control parameters
  - Orbital potentials
  - Advanced runtime cards
  - Scientific explanations
- **Scientific runtime output system** with:
  - Stored execution logs
  - Parsed scientific results
  - Computation history
- **User analytics dashboard**:
  - Computation history
  - Charts
  - Recent scientific activity
- **Administrative dashboard**:
  - Platform analytics
  - SEO management
  - Theory publishing
  - Runtime presets
- **SQLite support by default**
- **Preserved original X2DHF scientific source materials** for comparison and reference.

---

## Repository Name

Recommended repository name:

```text
x2dhf-scientific-cloud
```

---

## Project Structure

```text
.
├── manage.py
├── web
│   ├── backend
│   │   ├── requirements.txt
│   │   ├── db.sqlite3
│   │   └── x2dhf_project
│   └── frontend
│       ├── package.json
│       ├── src
│       └── build
├── src
├── include
├── test-sets
├── docs
├── hf_orbitals
└── lda_orbitals
```

---

## Requirements

### Supported Platforms

- Windows 10/11
- Linux

### Software Requirements

- Python **3.10+**
- Node.js **18+**
- PowerShell (Windows)

The web application runs through **Django**, while the default scientific runtime is **Python-based**, meaning no manual installation of:

- Fortran
- C/C++
- CMake
- WSL
- Libxc
- Quantum Espresso

is required for standard web-based usage.

---

## Installation

From repository root:

```powershell
cd C:\Users\Administrator\Downloads\x2dhf-main-website\x2dhf-main
```

### Create Backend Virtual Environment

```powershell
python -m venv web\backend\.venv
.\web\backend\.venv\Scripts\Activate.ps1
```

### Install Backend Dependencies

```powershell
pip install -r web\backend\requirements.txt
```

### Install Frontend Dependencies

```powershell
cd web\frontend
npm install
npm run build
cd ..\..
```

### Prepare Database

```powershell
python manage.py migrate
```

### Run the Platform

```powershell
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

## One-Command Startup

After initial dependency installation:

```powershell
.\web\backend\.venv\Scripts\Activate.ps1; python manage.py migrate; python manage.py runserver
```

---

## Authentication & Admin

No public admin credentials are distributed.

Create an administrator account:

```powershell
python manage.py createsuperuser
```

Login using:

```text
/admin-login
```

### Optional Local Development Admin

```powershell
$env:X2DHF_CREATE_DEV_ADMIN="1"
$env:X2DHF_ADMIN_EMAIL="your-admin@example.com"
$env:X2DHF_ADMIN_PASSWORD="change-this-password"
python manage.py runserver
```

---

## Scientific Workflow

### User Workflow

1. Register an account
2. Login
3. Open **Computations**
4. Select:
   - Atoms
   - Molecule mode
   - Theory
   - Functional
   - Grid
   - Orbital potentials
   - SCF controls
   - Advanced scientific cards
5. Run computation
6. Observe runtime output
7. Review stored results and analytics

### Administrative Workflow

1. Login through `/admin-login`
2. Access Admin Dashboard
3. Review platform analytics
4. Manage SEO metadata
5. Publish scientific theory posts
6. Create runtime presets

---

## Useful Commands

### Django Health Check

```powershell
.\web\backend\.venv\Scripts\python.exe manage.py check
```

### Run Tests

```powershell
.\web\backend\.venv\Scripts\python.exe -m pytest
```

### Rebuild Frontend

```powershell
cd web\frontend
npm run build
cd ..\..
```

### Apply Database Migrations

```powershell
.\web\backend\.venv\Scripts\python.exe manage.py migrate
```

---

## Configuration

Environment values can be placed inside:

```text
web/backend/.env
```

Example configuration:

```env
DEBUG=True
SECRET_KEY=change-this-for-production
DB_ENGINE=sqlite
AUTO_START_COMPUTATIONS=True
PYTHON_SCIENCE_RUNTIME=True
USE_NATIVE_X2DHF=False
X2DHF_CREATE_DEV_ADMIN=False
X2DHF_ADMIN_EMAIL=
X2DHF_ADMIN_PASSWORD=
```

---

## Production Deployment

Before deployment:

- Set `DEBUG=False`
- Replace `SECRET_KEY`
- Configure `ALLOWED_HOSTS`
- Move to PostgreSQL
- Configure static file serving
- Build frontend:

```powershell
npm run build
```

Collect static files:

```powershell
python manage.py collectstatic
```

Recommended deployment stack:

- **Gunicorn/Uvicorn**
- **Nginx**
- **Linux server environment**

---

## Scientific Scope

The repository preserves original **X2DHF scientific source materials**, orbital files, samples, and documentation.

The SaaS runtime is **Python-first** while preserving:

- X2DHF-style scientific input
- HF/DFT workflow methodology
- Scientific runtime outputs
- Computation history
- Guided quantum chemistry workflows

For validation against the original implementation, compare results using:

```text
src/
include/
test-sets/
docs/
hf_orbitals/
lda_orbitals/
```

---

## License

See:

```text
LICENSE
COPYING
```
