# StokTakip

A stock tracking system built with **Django 5 + Django REST Framework**, using
**Microsoft SQL Server** as the default database via
[mssql-django](https://github.com/microsoft/mssql-django).

Modules: categories, products, customers, orders (with items), stock movements,
and a customer ledger (*cari*). Ships with the Django admin, Django auth, a REST
API, and an order reporting endpoint.

## Quick start (Docker — recommended)

No local ODBC/SQL Server install needed; everything runs in containers.

```bash
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

- Admin: http://localhost:8000/admin
- API root: http://localhost:8000/api/
- Products: http://localhost:8000/api/products
- Report: http://localhost:8000/api/orders/report?period=daily&date=2026-07-08

The `web` container waits for SQL Server to be healthy, creates the `StokTakip`
database if it does not exist, runs migrations, and starts the dev server.

To stop / reset:

```bash
docker compose down        # stop
docker compose down -v     # stop and delete the SQL Server data volume
```

## Configuration

Configuration is environment-driven (loaded from `.env` via `python-dotenv`).
Copy the example and adjust as needed:

```bash
cp .env.example .env
```

| Variable              | Default                        | Notes                                   |
| --------------------- | ------------------------------ | --------------------------------------- |
| `DJANGO_SECRET_KEY`   | `change-me`                    | Set a long random value in production   |
| `DJANGO_DEBUG`        | `True`                         |                                         |
| `DJANGO_ALLOWED_HOSTS`| `localhost,127.0.0.1`          | Comma-separated                         |
| `DB_ENGINE`           | `mssql`                        | **MS SQL is the default**; `sqlite` to fall back |
| `DB_NAME`             | `StokTakip`                    |                                         |
| `DB_USER`             | `sa`                           |                                         |
| `DB_PASSWORD`         | `YourStrong!Passw0rd`          |                                         |
| `DB_HOST`             | `db` (compose) / `localhost`   |                                         |
| `DB_PORT`             | `1433`                         |                                         |
| `DB_ODBC_DRIVER`      | `ODBC Driver 18 for SQL Server`|                                         |
| `DB_EXTRA_PARAMS`     | `TrustServerCertificate=yes`   |                                         |

## Local run without Docker

Requires a reachable SQL Server plus the ODBC driver on the host.

### Windows

1. Install **Microsoft ODBC Driver 18 for SQL Server** (from Microsoft's site).
2. Create/point to a SQL Server instance and set `DB_HOST`/`DB_PORT`/credentials
   in `.env` (use `DB_HOST=localhost` when not using Docker).
3. Then:

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Linux/macOS

Install `msodbcsql18` (+ `unixodbc-dev`), create the database once
(`CREATE DATABASE StokTakip;`), then run the same `pip install` / `migrate` /
`runserver` steps above. To skip SQL Server entirely for a quick smoke test, set
`DB_ENGINE=sqlite`.

## API overview

Base path: `/api/`

| Resource         | Endpoint                | Access                         |
| ---------------- | ----------------------- | ------------------------------ |
| Categories       | `/api/categories/`      | Read: anyone · Write: staff    |
| Products         | `/api/products/`        | Read: anyone · Write: staff    |
| Customers        | `/api/customers/`       | Authenticated                  |
| Orders           | `/api/orders/`          | Authenticated                  |
| Stock movements  | `/api/stock-movements/` | Authenticated                  |
| Ledger (cari)    | `/api/ledger/`          | Authenticated                  |
| Order report     | `/api/orders/report`    | `?period=daily|weekly|monthly&date=YYYY-MM-DD` |

`Product` responses include a computed `stock_on_hand` (`in − out + adj`).

Creating an `Order` with nested `items` atomically also:
- creates an `out` `StockMovement` for each item, and
- adds a `LedgerEntry` for the customer with the order total as **credit**.

Example order payload:

```json
{
  "order_no": "ORD-001",
  "customer": 1,
  "status": "confirmed",
  "items": [
    {"product": 1, "qty": "2", "unit_price": "10.00"},
    {"product": 2, "qty": "1", "unit_price": "25.50"}
  ]
}
```

The report aggregates **confirmed** orders in the selected period and returns the
order count and total revenue.
