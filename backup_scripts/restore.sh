# backup_scripts/restore.sh
#!/bin/bash
# Backup Wiederherstellung

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_timestamp>"
    echo ""
    echo "Available backups:"
    ls -1 backups/django_data_*.json 2>/dev/null | sed 's/.*django_data_//' | sed 's/\.json//' | sort
    echo ""
    echo "Example: $0 20260105_1430"
    exit 1
fi

TIMESTAMP=$1
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="$PROJECT_DIR/backups"

echo "=== MoVi Restore ==="
echo "Wiederherstelle Backup vom: $TIMESTAMP"
echo ""

# Prüfe ob Backup existiert
if [ ! -f "$BACKUP_DIR/django_data_${TIMESTAMP}.json" ]; then
    echo "ERROR: Backup nicht gefunden!"
    echo "Gesucht: $BACKUP_DIR/django_data_${TIMESTAMP}.json"
    exit 1
fi

echo "Gefundene Backup-Dateien:"
ls -la "$BACKUP_DIR"/*${TIMESTAMP}* 2>/dev/null

# Sicherheitsabfrage
echo ""
read -p "⚠️  WARNUNG: Dies überschreibt alle aktuellen Daten! Fortfahren? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Abgebrochen."
    exit 0
fi

echo ""
echo "1. Docker Services stoppen..."
docker-compose stop web

echo ""
echo "2. Datenbank zurücksetzen..."

# PostgreSQL Restore
DB_CONTAINER=$(docker-compose ps -q db)
if [ -n "$DB_CONTAINER" ]; then
    echo "   Datenbank löschen und neu erstellen..."

    # Drop und recreate database
    docker exec $DB_CONTAINER psql -U django_user -d postgres -c "
        DROP DATABASE IF EXISTS django_db;
        CREATE DATABASE django_db;
    " 2>/dev/null || true

    echo "   ✅ Datenbank zurückgesetzt"
fi

echo ""
echo "3. Django Daten wiederherstellen..."

WEB_CONTAINER=$(docker-compose ps -q web)
if [ -n "$WEB_CONTAINER" ]; then
    # Backup in Container kopieren
    docker cp "$BACKUP_DIR/django_data_${TIMESTAMP}.json" $WEB_CONTAINER:/tmp/restore_data.json

    # Datenbank migrieren
    docker exec $WEB_CONTAINER python manage.py migrate --noinput

    # Daten laden
    docker exec $WEB_CONTAINER python manage.py loaddata /tmp/restore_data.json

    echo "   ✅ Django Daten wiederhergestellt"
fi

echo ""
echo "4. Services neu starten..."
docker-compose start web

echo ""
echo "✅ Wiederherstellung abgeschlossen!"
echo "   Backup: $TIMESTAMP"
echo "   Zeit: $(date)"
echo ""
echo "Tipp: Prüfen Sie die Anwendung unter http://localhost:8000"