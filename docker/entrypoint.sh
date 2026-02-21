#!/bin/bash
set -e

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Wait for PostgreSQL if nc is available
if command_exists nc; then
    echo "Waiting for PostgreSQL at $POSTGRES_HOST:5432..."
    while ! nc -z "$POSTGRES_HOST" 5432; do
        sleep 0.5
    done
    echo "PostgreSQL is reachable."
else
    echo "Warning: nc (netcat) not found. Skipping PostgreSQL reachability check."
fi

# Skip migrations in CI or test mode
if [[ "$CI" != "true" && "$@" != *"test"* ]]; then
    echo "Running database migrations..."
    python manage.py makemigrations --noinput || true
    python manage.py migrate
else
    echo "Skipping migrations (CI mode or test run)."
fi

# Execute the CMD passed to the container
exec "$@"
