# backup_scripts/backup_manager.py
"""
BSI CON.3.A1: Backup Management - Host Version
"""
import os
import json
import subprocess
import tarfile
from datetime import datetime, timedelta
import sys


class HostBackupManager:
    def __init__(self, project_dir=None):
        if project_dir is None:
            project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.project_dir = project_dir
        self.backup_dir = os.path.join(project_dir, "backups")
        self.scripts_dir = os.path.join(project_dir, "backup_scripts")

        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(self.scripts_dir, exist_ok=True)

    def run_docker_command(self, cmd):
        """Führt einen Docker Befehl aus"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Timeout expired"
        except Exception as e:
            return False, "", str(e)

    def backup_postgresql(self):
        """PostgreSQL Datenbank sichern"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.backup_dir, f"postgres_backup_{timestamp}.sql")

        print(f"Creating PostgreSQL backup: {backup_file}")

        # pg_dump via docker exec
        cmd = f"docker-compose exec -T db pg_dumpall -U django_user"

        success, stdout, stderr = self.run_docker_command(cmd)

        if success:
            with open(backup_file, 'w') as f:
                f.write(stdout)

            size = os.path.getsize(backup_file)
            print(f"  ✅ PostgreSQL backup created ({size:,} bytes)")
            return backup_file
        else:
            print(f"  ❌ PostgreSQL backup failed: {stderr}")
            return None

    def backup_django_data(self):
        """Django Daten als JSON exportieren"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.backup_dir, f"django_data_{timestamp}.json")

        print(f"Creating Django data backup: {backup_file}")

        # dumpdata via docker exec
        cmd = (
            "docker-compose exec -T web python manage.py dumpdata "
            "--exclude=contenttypes --exclude=auth.permission "
            "--exclude=admin.logentry --exclude=sessions.session --indent=2"
        )

        success, stdout, stderr = self.run_docker_command(cmd)

        if success and stdout.strip():
            with open(backup_file, 'w') as f:
                f.write(stdout)

            size = os.path.getsize(backup_file)
            print(f"  ✅ Django data backup created ({size:,} bytes)")
            return backup_file
        else:
            print(f"  ⚠️  Django data backup may be empty: {stderr[:100]}")
            return None

    def create_backup_report(self):
        """Backup Report generieren"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(self.backup_dir, f"backup_report_{timestamp}.json")

        # System Info sammeln
        report = {
            "timestamp": timestamp,
            "project": "MoVi - Semantic Movie Search",
            "backup_location": self.backup_dir,
            "docker_status": {},
            "backup_files": [],
            "total_size_mb": 0
        }

        # Docker Status
        success, stdout, stderr = self.run_docker_command("docker-compose ps")
        if success:
            report["docker_status"] = stdout.strip().split('\n')

        # Backup Dateien auflisten
        total_size = 0
        for filename in os.listdir(self.backup_dir):
            if timestamp in filename:
                filepath = os.path.join(self.backup_dir, filename)
                size = os.path.getsize(filepath)
                total_size += size
                report["backup_files"].append({
                    "name": filename,
                    "size_bytes": size,
                    "size_human": self.human_readable_size(size)
                })

        report["total_size_mb"] = round(total_size / (1024 * 1024), 2)

        # Report speichern
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"  ✅ Backup report created: {report_file}")
        return report

    def human_readable_size(self, size_bytes):
        """Bytes in lesbare Größe umwandeln"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def cleanup_old_backups(self, days_to_keep=7):
        """Alte Backups löschen"""
        cutoff = datetime.now() - timedelta(days=days_to_keep)
        deleted_count = 0

        for filename in os.listdir(self.backup_dir):
            filepath = os.path.join(self.backup_dir, filename)
            if os.path.isfile(filepath):
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                if mtime < cutoff:
                    os.remove(filepath)
                    deleted_count += 1
                    print(f"  Deleted old backup: {filename}")

        print(f"  ✅ Cleanup: {deleted_count} old backups deleted")
        return deleted_count

    def run_full_backup(self):
        """Vollständiges Backup durchführen"""
        print("=" * 50)
        print("MoVi Backup System - BSI CON.3.A1")
        print("=" * 50)
        print(f"Project: {self.project_dir}")
        print(f"Backup Dir: {self.backup_dir}")
        print()

        # 1. Backups erstellen
        pg_backup = self.backup_postgresql()
        django_backup = self.backup_django_data()

        print()

        # 2. Report erstellen
        report = self.create_backup_report()

        print()

        # 3. Cleanup
        self.cleanup_old_backups()

        print()
        print("=" * 50)
        print("Backup completed successfully!")
        print(f"Total backup size: {report['total_size_mb']} MB")
        print(f"Backup files: {len(report['backup_files'])}")
        print(f"Location: {self.backup_dir}")
        print("=" * 50)

        return report


# CLI Interface
if __name__ == "__main__":
    manager = HostBackupManager()

    if len(sys.argv) > 1:
        if sys.argv[1] == "run":
            manager.run_full_backup()
        elif sys.argv[1] == "list":
            print("Available backups:")
            for f in sorted(os.listdir(manager.backup_dir)):
                if f.endswith('.json') or f.endswith('.sql'):
                    path = os.path.join(manager.backup_dir, f)
                    size = os.path.getsize(path)
                    mtime = datetime.fromtimestamp(os.path.getmtime(path))
                    print(f"  {f} - {manager.human_readable_size(size)} - {mtime}")
        elif sys.argv[1] == "cleanup":
            deleted = manager.cleanup_old_backups()
            print(f"Deleted {deleted} old backups")
        elif sys.argv[1] == "test":
            print("Testing backup system...")
            manager.backup_postgresql()
            manager.backup_django_data()
        else:
            print(f"Unknown command: {sys.argv[1]}")
    else:
        print("Usage: python backup_manager.py [run|list|cleanup|test]")
        print("  run     - Full backup")
        print("  list    - List available backups")
        print("  cleanup - Remove old backups (>7 days)")
        print("  test    - Test backup functions")