#!/bin/bash
# entrypoint.sh

# Warten auf PostgreSQL
echo "Warte auf PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL ist bereit!"

# Migrationen ausführen
echo "Führe Migrationen aus..."
python manage.py makemigrations
python manage.py migrate

# Superuser erstellen (falls noch nicht vorhanden)
echo "Erstelle Superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser erstellt: admin/admin123')
else:
    print('Superuser existiert bereits')
"

exec "$@"