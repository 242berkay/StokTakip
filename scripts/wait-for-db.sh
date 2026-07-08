#!/usr/bin/env bash
# Blocks until the SQL Server instance accepts connections.
set -e

DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-1433}"
DB_USER="${DB_USER:-sa}"

echo "Waiting for SQL Server at ${DB_HOST}:${DB_PORT}..."
until sqlcmd -S "${DB_HOST},${DB_PORT}" -U "${DB_USER}" -P "${DB_PASSWORD}" -C -Q "SELECT 1" -b -o /dev/null 2>/dev/null; do
  echo "  SQL Server is unavailable - sleeping"
  sleep 3
done
echo "SQL Server is up."
