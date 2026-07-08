# StokTakip

A Django + Django REST Framework inventory ("stok takip") project with Microsoft
SQL Server support via [mssql-django](https://github.com/microsoft/mssql-django).

## Features

- Django 6 project (`stoktakip`) with an `inventory` app.
- REST API for `Category` and `Product` resources (DRF `ModelViewSet` + router).
- Django admin registered for both models.
- Environment-based configuration (`.env`) that switches between SQLite (local
  dev) and Microsoft SQL Server.

## Requirements

- Python 3.10+ (developed on 3.12)
- For MS SQL: a running SQL Server instance and the **Microsoft ODBC Driver 18
  for SQL Server** installed on the machine running Django.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # then edit .env
```

## Database configuration

Configuration is driven by environment variables (loaded from `.env`).

### SQLite (default, for local development)

```env
DB_ENGINE=sqlite
```

### Microsoft SQL Server

```env
DB_ENGINE=mssql
DB_NAME=StokTakip
DB_USER=sa
DB_PASSWORD=YourStrong!Passw0rd
DB_HOST=localhost
DB_PORT=1433
DB_ODBC_DRIVER=ODBC Driver 18 for SQL Server
DB_EXTRA_PARAMS=TrustServerCertificate=yes
```

Install the ODBC driver:

- **Ubuntu/Debian:** follow Microsoft's guide for `msodbcsql18` and
  `unixODBC-dev`.
- **Windows:** download and install "ODBC Driver 18 for SQL Server" from
  Microsoft.
- **macOS:** `brew install msodbcsql18` (via the Microsoft Homebrew tap).

Create the database once on the server (mssql-django will not create it for you):

```sql
CREATE DATABASE StokTakip;
```

## Running

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

- API root: http://127.0.0.1:8000/api/
- Admin: http://127.0.0.1:8000/admin/
- Browsable API login: http://127.0.0.1:8000/api-auth/login/

## API endpoints

| Method            | Endpoint               | Description        |
| ----------------- | ---------------------- | ------------------ |
| GET/POST          | `/api/categories/`     | List/create categories |
| GET/PUT/PATCH/DEL | `/api/categories/{id}/`| Retrieve/update/delete |
| GET/POST          | `/api/products/`       | List/create products   |
| GET/PUT/PATCH/DEL | `/api/products/{id}/`  | Retrieve/update/delete |
