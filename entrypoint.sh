#!/bin/bash
set -e

echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."
until python -c "
import psycopg, sys
try:
    psycopg.connect(host='$DB_HOST', port=$DB_PORT, user='$DB_USER', password='$DB_PASSWORD', dbname='$DB_NAME')
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; do
    sleep 1
done
echo "PostgreSQL is ready."

echo "Running migrations..."
alembic upgrade head

echo "Starting app..."
exec python -m app.main
