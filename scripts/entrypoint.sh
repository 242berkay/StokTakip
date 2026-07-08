#!/usr/bin/env bash
set -e

DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-1433}"
DB_USER="${DB_USER:-sa}"
DB_NAME="${DB_NAME:-StokTakip}"

# Wait until SQL Server is reachable.
/app/scripts/wait-for-db.sh

# mssql-django does not create the database; create it once if missing.
echo "Ensuring database [${DB_NAME}] exists..."
sqlcmd -S "${DB_HOST},${DB_PORT}" -U "${DB_USER}" -P "${DB_PASSWORD}" -C \
  -Q "IF DB_ID('${DB_NAME}') IS NULL CREATE DATABASE [${DB_NAME}];"

# Run the container command (see docker-compose.yml). Falls back to a sane
# default when none is provided.
if [ "$#" -eq 0 ]; then
  set -- sh -c "python manage.py migrate && python manage.py ensure_superuser && python manage.py runserver 0.0.0.0:8000"
fi
exec "$@"
