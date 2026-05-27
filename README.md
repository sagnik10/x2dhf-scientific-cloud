# X2DHF Scientific Cloud

Python-first Django and React SaaS workspace for X2DHF-style Hartree-Fock and DFT computations, guided input cards, saved runtime output, user dashboards, admin analytics, theory publishing, and runtime control presets.

Recommended repository name:

```text
x2dhf-scientific-cloud
```

## Features

- Django 4 backend with JWT authentication.
- React frontend served by Django in `runserver` mode.
- Python quantum runtime for HF, DFT, HFS, OED, TED, SCMC, and Quantum Espresso-style workflows.
- X2DHF-style input builder with atoms, molecules, grid cards, SCF controls, orbital potentials, advanced cards, and explanations.
- Runtime output panel with stored logs and parsed scientific results.
- User dashboard with analytics, history, charts, and recent actions.
- Staff-only admin dashboard with platform analytics, SEO tools, theory post publishing, and runtime control presets.
- Local SQLite database by default.
- Optional original X2DHF Fortran/C reference files remain in the repository for comparison and source material.

## Project Layout

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

## Requirements

- Windows 10/11 or Linux
- Python 3.10+
- Node.js 18+
- PowerShell on Windows

The web application runs through Django. The default runtime is Python-based, so no manual Fortran, C, CMake, WSL, Libxc, or Quantum Espresso installation is required for normal website use.

## Fresh Installation

From the repository root:

```powershell
cd C:\Users\Administrator\Downloads\x2dhf-main-website\x2dhf-main
```

Create and activate the backend virtual environment:

```powershell
python -m venv web\backend\.venv
.\web\backend\.venv\Scripts\Activate.ps1
```

Install backend dependencies:

```powershell
pip install -r web\backend\requirements.txt
```

Install frontend dependencies:

```powershell
cd web\frontend
npm install
npm run build
cd ..\..
```

Prepare the database:

```powershell
python manage.py migrate
```

Run the full software:

```powershell
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## One Command After Setup

After dependencies are installed and the virtual environment exists:

```powershell
.\web\backend\.venv\Scripts\Activate.ps1; python manage.py migrate; python manage.py runserver
```

## Admin Login

No public default admin username or password is shipped.

Create a staff/superuser account from the server:

```powershell
python manage.py createsuperuser
```

Use `/admin-login` after creating the admin account.

For local-only development, automatic dev-admin creation is opt-in and requires all values below:

```powershell
$env:X2DHF_CREATE_DEV_ADMIN="1"
$env:X2DHF_ADMIN_EMAIL="your-admin@example.com"
$env:X2DHF_ADMIN_PASSWORD="change-this-password"
python manage.py runserver
```

## Normal User Flow

1. Register a user account.
2. Login.
3. Open `Computations`.
4. Choose atoms, molecule mode, theory, functional, grid, orbital potential, SCF limits, and advanced cards.
5. Run computation.
6. Watch runtime output.
7. Review saved results and dashboard analytics.

## Admin Flow

1. Login through `/admin-login`.
2. Open Admin.
3. Review platform analytics and theory usage.
4. Manage SEO metadata.
5. Publish theory posts.
6. Create runtime control presets for guided scientific workflows.

## Useful Commands

Backend check:

```powershell
.\web\backend\.venv\Scripts\python.exe manage.py check
```

Run tests:

```powershell
.\web\backend\.venv\Scripts\python.exe -m pytest
```

Rebuild frontend:

```powershell
cd web\frontend
npm run build
cd ..\..
```

Apply migrations:

```powershell
.\web\backend\.venv\Scripts\python.exe manage.py migrate
```

## Configuration

Backend environment values can be placed in:

```text
web/backend/.env
```

Common values:

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

## Production Notes

Before production deployment:

- Set `DEBUG=False`.
- Replace `SECRET_KEY`.
- Use PostgreSQL instead of SQLite.
- Configure `ALLOWED_HOSTS`.
- Configure static file serving.
- Run `npm run build`.
- Run `python manage.py collectstatic`.
- Use a real process manager such as Gunicorn/Uvicorn plus Nginx on Linux.
- Replace local admin credentials.

## Scientific Scope

The original X2DHF folders, samples, orbitals, and documentation remain in this checkout. The SaaS runtime is Python-first and designed to preserve X2DHF-style input/output structure, guided HF/DFT workflows, and stored computation history inside a web application.

For strict validation against the original Fortran/C implementation, compare against the reference files in:

```text
src/
include/
test-sets/
docs/
hf_orbitals/
lda_orbitals/
```

## License

See `LICENSE` and `COPYING`.
