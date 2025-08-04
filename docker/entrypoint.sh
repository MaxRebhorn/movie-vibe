#!/bin/bash
set -e

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
while ! nc -z $POSTGRES_HOST 5432; do
  sleep 0.5
done
echo "PostgreSQL is reachable."

# Run migrations for all commands except test
if [[ "$@" != *"test"* ]]; then
  echo "Running database migrations..."
  python manage.py makemigrations --noinput
  python manage.py migrate
fi

exec "$@"