#!/bin/bash

# Warte auf Datenbank
echo "Warte auf Datenbank..."
while ! nc -z $POSTGRES_HOST 5432; do sleep 0.5; done
echo "PostgreSQL ist erreichbar."

# Warte auf Elasticsearch (mit Timeout)
echo "Warte auf Elasticsearch..."
timeout=30
while ! curl -s http://elasticsearch:9200 >/dev/null; do
  sleep 1
  timeout=$((timeout-1))
  [ $timeout -le 0 ] && echo "Elasticsearch Timeout!" && exit 1
done
echo "Elasticsearch ist erreichbar."

# Django-Setup
echo "Führe Migrationen durch..."
python manage.py migrate

echo "Erstelle Elasticsearch-Indizes..."
python manage.py search_index --rebuild -f || echo "Warnung: search_index fehlgeschlagen"

echo "Prüfe Django-Setup..."
python manage.py check

echo "Starte den Server..."
exec "$@"