# Django REST API

A minimal Django REST Framework API foundation with a public health check.

## Setup

Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

```powershell
python manage.py migrate
python manage.py runserver
```

The API is available at `http://127.0.0.1:8000/api/health/` and returns `{"status":"ok"}`.

## PostgreSQL

PostgreSQL is the configured database. Set these PowerShell environment variables before running migrations:

```powershell
$env:POSTGRES_DB = "api_db"
$env:POSTGRES_USER = "postgres"
$env:POSTGRES_PASSWORD = "<your-password>"
$env:POSTGRES_HOST = "localhost"
$env:POSTGRES_PORT = "5432"
python manage.py migrate
```

Create the database in PostgreSQL first if it does not already exist. Keep credentials out of source control.

## Configuration

Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, and `DJANGO_ALLOWED_HOSTS` in the environment before deployment. The built-in secret and debug defaults are for local development only. PostgreSQL connection values use the `POSTGRES_*` variables documented above.