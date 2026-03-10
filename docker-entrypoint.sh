#!/bin/bash
# PatosGym — Docker Entrypoint
# Relies on docker-compose 'healthcheck' + 'depends_on: condition: service_healthy'
# to ensure PostgreSQL is ready before this runs.
set -e

echo "==> Running database migrations..."
python manage.py migrate --noinput

echo "==> Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "==> Starting application..."
exec "$@"
