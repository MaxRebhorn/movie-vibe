# backup_scripts/backup.sh
#!/bin/bash
# BSI CON.3.A1: Backup Script für MoVi - Läuft auf dem Host

set -e

echo "=== MoVi Backup System ==="
echo "Start: $(date)"
echo ""

# Konfiguration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="$PROJECT_DIR/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$BACKUP_DIR/backup_${TIMESTAMP}.log"

# Verzeichnis sicherstellen
mkdir -p "$BACKUP_DIR"

echo "1. Docker Container Status prüfen..." | tee "$LOG_FILE"
docker-compose ps | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "2. PostgreSQL Datenbank exportieren..." | tee -a "$LOG_FILE"

# PostgreSQL Backup mit docker exec
DB_CONTAINER=$(docker-compose ps -q db)
if [ -n "$DB_CONTAINER" ]; then
    docker exec $DB_CONTAINER pg_dumpall -U django_user > "$BACKUP_DIR/full_database_${TIMESTAMP}.sql" 2>> "$LOG_FILE"

    if [ $? -eq 0 ]; then
        DB_SIZE=$(stat -f%z "$BACKUP_DIR/full_database_${TIMESTAMP}.sql" 2>/dev/null || stat -c%s "$BACKUP_DIR/full_database_${TIMESTAMP}.sql")
        echo "   ✅ PostgreSQL Backup erstellt: $BACKUP_DIR/full_database_${TIMESTAMP}.sql ($DB_SIZE bytes)" | tee -a "$LOG_FILE"
    else
        echo "   ❌ PostgreSQL Backup fehlgeschlagen" | tee -a "$LOG_FILE"
    fi
else
    echo "   ⚠️  DB Container nicht gefunden" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"
echo "3. Django Daten exportieren (JSON)..." | tee -a "$LOG_FILE"

# Django dumpdata via docker exec
WEB_CONTAINER=$(docker-compose ps -q web)
if [ -n "$WEB_CONTAINER" ]; then
    docker exec $WEB_CONTAINER python manage.py dumpdata \
        --exclude=contenttypes \
        --exclude=auth.permission \
        --exclude=admin.logentry \
        --exclude=sessions.session \
        --indent=2 \
        --output="/tmp/django_data_${TIMESTAMP}.json" 2>> "$LOG_FILE"

    # Datei aus Container kopieren
    docker cp $WEB_CONTAINER:/tmp/django_data_${TIMESTAMP}.json "$BACKUP_DIR/" 2>> "$LOG_FILE"

    if [ -f "$BACKUP_DIR/django_data_${TIMESTAMP}.json" ]; then
        JSON_SIZE=$(stat -f%z "$BACKUP_DIR/django_data_${TIMESTAMP}.json" 2>/dev/null || stat -c%s "$BACKUP_DIR/django_data_${TIMESTAMP}.json")
        echo "   ✅ Django Data Backup: $BACKUP_DIR/django_data_${TIMESTAMP}.json ($JSON_SIZE bytes)" | tee -a "$LOG_FILE"
    else
        echo "   ❌ Django Data Backup fehlgeschlagen" | tee -a "$LOG_FILE"
    fi
fi

echo "" | tee -a "$LOG_FILE"
echo "4. Docker Volumes sichern..." | tee -a "$LOG_FILE"

# Liste der Volumes
VOLUMES=$(docker volume ls -q --filter name=movie-vibe)

for VOLUME in $VOLUMES; do
    echo "   Volume: $VOLUME" | tee -a "$LOG_FILE"

    # Volume-Inhalt auflisten (nur Info)
    docker run --rm -v $VOLUME:/volume alpine ls -la /volume 2>> "$LOG_FILE" | head -5 | tee -a "$LOG_FILE"
done

echo "" | tee -a "$LOG_FILE"
echo "5. Backup-Info erstellen..." | tee -a "$LOG_FILE"

# Backup-Info Datei
cat > "$BACKUP_DIR/backup_info_${TIMESTAMP}.txt" << EOF
MoVi Backup Report
==================
Backup Time: $(date)
Backup ID: $TIMESTAMP
Location: $BACKUP_DIR

Files:
$(ls -la "$BACKUP_DIR"/*${TIMESTAMP}* 2>/dev/null | awk '{print $5, $9}')

Docker Status:
$(docker-compose ps)

System Info:
$(uname -a)
EOF

echo "   ✅ Backup Info: $BACKUP_DIR/backup_info_${TIMESTAMP}.txt" | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "6. Alte Backups bereinigen (älter als 7 Tage)..." | tee -a "$LOG_FILE"

find "$BACKUP_DIR" -name "*.sql" -mtime +7 -delete 2>> "$LOG_FILE"
find "$BACKUP_DIR" -name "*.json" -mtime +7 -delete 2>> "$LOG_FILE"
find "$BACKUP_DIR" -name "*.txt" -mtime +7 -delete 2>> "$LOG_FILE"
find "$BACKUP_DIR" -name "*.log" -mtime +30 -delete 2>> "$LOG_FILE"

echo "   ✅ Cleanup abgeschlossen" | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "=== Backup abgeschlossen ===" | tee -a "$LOG_FILE"
echo "Backup Verzeichnis: $BACKUP_DIR" | tee -a "$LOG_FILE"
echo "Log Datei: $LOG_FILE" | tee -a "$LOG_FILE"
echo "Backup Dateien:" | tee -a "$LOG_FILE"
ls -lh "$BACKUP_DIR"/*${TIMESTAMP}* 2>/dev/null | tee -a "$LOG_FILE"


