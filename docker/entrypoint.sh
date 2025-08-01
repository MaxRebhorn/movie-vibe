#!/bin/bash
set -e

# Wait for PostgreSQL
echo "Waiting for PostgreSQL at $POSTGRES_HOST:5432..."
while ! nc -z "$POSTGRES_HOST" 5432; do
  sleep 0.5
done
echo "PostgreSQL is reachable."

# Skip migrations in CI or when running tests
if [[ "$CI" != "true" && "$@" != *"test"* ]]; then
  echo "Running database migrations..."
  python manage.py makemigrations --noinput
  python manage.py migrate
else
  echo "Skipping migrations (CI mode or test run)."
fi

exec "$@"
