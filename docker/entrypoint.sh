#!/bin/bash
set -e

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
while ! nc -z $POSTGRES_HOST 5432; do
  sleep 0.5
done
echo "PostgreSQL is reachable."

# Wait for Elasticsearch cluster health
echo "Waiting for Elasticsearch cluster health..."
timeout=120
while ! curl -fs http://elasticsearch:9200/_cluster/health?pretty | \
  grep -q "\"status\" : \"\(green\|yellow\)\""; do
  sleep 5
  timeout=$((timeout-5))
  if [ $timeout -le 0 ]; then
    echo "Elasticsearch health check timeout!"
    exit 1
  fi
  echo "Waiting for Elasticsearch (${timeout}s remaining)..."
done
echo "Elasticsearch cluster is healthy."

# Django setup
echo "Running migrations..."
python manage.py migrate

echo "Creating Elasticsearch indices..."
python manage.py search_index --rebuild -f || {
  echo "Warning: search_index command failed"
  # Don't exit on this failure as it might be non-critical
}

echo "Checking Django setup..."
python manage.py check

echo "Starting server..."
exec "$@"