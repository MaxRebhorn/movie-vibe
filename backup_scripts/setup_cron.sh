# backup_scripts/setup_cron.sh
#!/bin/bash
# Einrichtung automatischer Backups

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CRON_JOB="0 2 * * * cd $PROJECT_DIR && $PROJECT_DIR/backup_scripts/backup.sh >> $PROJECT_DIR/backups/cron.log 2>&1"

echo "Setting up automatic backups for MoVi..."
echo ""
echo "Cron Job:"
echo "$CRON_JOB"
echo ""

# In Crontab eintragen
(crontab -l 2>/dev/null | grep -v "backup.sh"; echo "$CRON_JOB") | crontab -

echo "Cron job installed successfully!"
echo ""
echo "Current crontab:"
crontab -l | grep backup
echo ""
echo "Manual backup: ./backup_scripts/backup.sh"
echo "Python backup: python backup_scripts/backup_manager.py run"