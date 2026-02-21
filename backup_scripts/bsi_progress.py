# backup_scripts/bsi_progress.py
"""
BSI Grundschutz - Fortschrittsanalyse für MoVi
Aktualisiert: 05.01.2026
"""

import os
import json
import subprocess
from datetime import datetime


class BSIProgressTracker:
    def __init__(self, project_dir=None):
        if project_dir is None:
            project_dir = os.getcwd()
        self.project_dir = project_dir

    def check_network_segmentation(self):
        """Prüft BSI NET.1.1.A3: Netzwerksegmentierung"""
        print("🔍 Prüfe NET.1.1.A3: Netzwerksegmentierung...")

        checks = {
            "docker_compose_exists": os.path.exists("docker-compose.yml"),
            "web_port_exposed": False,
            "db_port_localhost_only": False,
            "elasticsearch_not_exposed": False,
            "qdrant_not_exposed": False
        }

        try:
            # Docker Compose lesen
            with open("docker-compose.yml", "r") as f:
                content = f.read()

            # Prüfe Port Konfigurationen
            checks["web_port_exposed"] = "8000:8000" in content
            checks["db_port_localhost_only"] = "127.0.0.1:5432:5432" in content or "5432:5432" not in content
            checks["elasticsearch_not_exposed"] = "9200:9200" not in content and "127.0.0.1:9200:9200" not in content
            checks["qdrant_not_exposed"] = "6333:6333" not in content and "127.0.0.1:6333:6333" not in content

            # Netzwerk-Konfiguration prüfen
            if "networks:" in content and ("backend_network" in content or "frontend_network" in content):
                checks["network_segmentation"] = True
            else:
                checks["network_segmentation"] = False

        except Exception as e:
            print(f"   Fehler bei Netzwerkprüfung: {e}")
            checks["network_segmentation"] = False

        return checks

    def check_backup_system(self):
        """Prüft BSI CON.3.A1: Regelmäßige Backups"""
        print("🔍 Prüfe CON.3.A1: Backup-System...")

        checks = {
            "backup_dir_exists": os.path.exists("backups"),
            "backup_scripts_exist": False,
            "backup_sh_exists": False,
            "restore_sh_exists": False,
            "backup_manager_exists": False,
            "backup_files_exist": False
        }

        # Prüfe Verzeichnisse
        checks["backup_scripts_exist"] = os.path.exists("backup_scripts")

        # Prüfe einzelne Dateien
        if checks["backup_scripts_exist"]:
            checks["backup_sh_exists"] = os.path.exists("backup_scripts/backup.sh")
            checks["restore_sh_exists"] = os.path.exists("backup_scripts/restore.sh")
            checks["backup_manager_exists"] = os.path.exists("backup_scripts/backup_manager.py")

        # Prüfe ob Backup-Dateien existieren
        if checks["backup_dir_exists"]:
            backup_files = [f for f in os.listdir("backups") if not f.startswith(".")]
            checks["backup_files_exist"] = len(backup_files) > 0
            checks["backup_file_count"] = len(backup_files)

        # Prüfe Cron Setup (optional)
        try:
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            checks["cron_configured"] = "backup.sh" in result.stdout
        except:
            checks["cron_configured"] = False

        return checks

    def check_cors_security(self):
        """Prüft BSI ORP.4.A1: Zugriffskontrolle (CORS)"""
        print("🔍 Prüfe ORP.4.A1: CORS Sicherheit...")

        checks = {
            "settings_exists": os.path.exists("django_backend/settings.py"),
            "cors_allow_all_origins": False,
            "cors_allowed_origins": False,
            "csrf_trusted_origins": False
        }

        try:
            with open("django_backend/settings.py", "r") as f:
                content = f.read()

            # Entwicklungs-Konfiguration (erwartet)
            checks["cors_allow_all_origins"] = "CORS_ALLOW_ALL_ORIGINS = True" in content
            checks["cors_allowed_origins"] = "CORS_ALLOWED_ORIGINS" in content
            checks["csrf_trusted_origins"] = "CSRF_TRUSTED_ORIGINS" in content

        except Exception as e:
            print(f"   Fehler bei CORS-Prüfung: {e}")

        return checks

    def check_security_headers(self):
        """Prüft allgemeine Sicherheitsmaßnahmen"""
        print("🔍 Prüfe allgemeine Sicherheit...")

        checks = {
            "debug_disabled_in_prod": False,
            "csrf_protection": False,
            "session_cookie_secure": False,
            "rate_limiting": False
        }

        try:
            with open("django_backend/settings.py", "r") as f:
                content = f.read()

            checks["debug_disabled_in_prod"] = "DEBUG = False" in content or "# DEBUG = True" in content
            checks["csrf_protection"] = "'django.middleware.csrf.CsrfViewMiddleware'" in content
            checks["session_cookie_secure"] = "SESSION_COOKIE_SECURE = True" in content
            checks["rate_limiting"] = "DEFAULT_THROTTLE_RATES" in content or "throttling" in content.lower()

        except Exception as e:
            print(f"   Fehler bei Security-Header Prüfung: {e}")

        return checks

    def generate_report(self):
        """Generiert einen vollständigen BSI-Report"""
        print("=" * 60)
        print("BSI GRUNDSCHUTZ ANALYSE - MoVi")
        print("=" * 60)
        print(f"Datum: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        print()

        # Alle Checks durchführen
        network_checks = self.check_network_segmentation()
        backup_checks = self.check_backup_system()
        cors_checks = self.check_cors_security()
        security_checks = self.check_security_headers()

        # BSI Bausteine bewerten
        bsi_results = {
            "NET.1.1.A3": {
                "name": "Netzwerksegmentierung",
                "checks": network_checks,
                "AIContext.txt": self._evaluate_status(network_checks, required=["network_segmentation", "web_port_exposed"]),
                "score": self._calculate_score(network_checks)
            },
            "CON.3.A1": {
                "name": "Regelmäßige Backups",
                "checks": backup_checks,
                "AIContext.txt": self._evaluate_status(backup_checks, required=["backup_dir_exists", "backup_sh_exists"]),
                "score": self._calculate_score(backup_checks)
            },
            "ORP.4.A1": {
                "name": "Zugriffskontrolle (CORS)",
                "checks": cors_checks,
                "AIContext.txt": self._evaluate_status(cors_checks, required=["settings_exists"]),
                "score": self._calculate_score(cors_checks),
                "note": "Für Entwicklung deaktiviert"
            },
            "APP.3.1.A1": {
                "name": "Webanwendungssicherheit",
                "checks": security_checks,
                "AIContext.txt": self._evaluate_status(security_checks, required=["csrf_protection"]),
                "score": self._calculate_score(security_checks)
            }
        }

        # Report anzeigen
        self._print_detailed_report(bsi_results)

        # JSON Report speichern
        self._save_json_report(bsi_results)

        return bsi_results

    def _evaluate_status(self, checks, required=None):
        """Bewertet den Status basierend auf Checks"""
        if required is None:
            required = []

        # Zähle erfolgreiche Checks
        total = len(checks)
        passed = sum(1 for check, value in checks.items() if value is True)

        # Prüfe required Checks
        all_required_passed = all(checks.get(req, False) for req in required)

        if all_required_passed and passed / total >= 0.8:
            return "✅ ERFÜLLT"
        elif all_required_passed and passed / total >= 0.5:
            return "⚠️ TEILWEISE"
        else:
            return "❌ NICHT ERFÜLLT"

    def _calculate_score(self, checks):
        """Berechnet einen Score (0-100)"""
        total = len(checks)
        passed = sum(1 for value in checks.values() if value is True)
        return int((passed / total) * 100) if total > 0 else 0

    def _print_detailed_report(self, bsi_results):
        """Detaillierten Report ausgeben"""
        print("BSI BAUSTEINE - DETAILÜBERSICHT")
        print("=" * 60)

        overall_score = 0
        total_items = 0

        for baustein, data in bsi_results.items():
            print(f"\n{baustein}: {data['name']}")
            print(f"Status: {data['AIContext.txt']} (Score: {data['score']}/100)")

            if "note" in data:
                print(f"Hinweis: {data['note']}")

            print("Einzelprüfungen:")
            for check, value in data["checks"].items():
                icon = "✓" if value else "✗"
                print(f"  {icon} {check}: {value}")

            overall_score += data['score']
            total_items += 1

        print("\n" + "=" * 60)
        print("ZUSAMMENFASSUNG")
        print("=" * 60)

        # Gesamtbewertung
        avg_score = overall_score / total_items if total_items > 0 else 0

        if avg_score >= 80:
            rating = "SEHR GUT"
            color = "\033[92m"  # Green
        elif avg_score >= 60:
            rating = "GUT"
            color = "\033[93m"  # Yellow
        elif avg_score >= 40:
            rating = "BEFRIEDIGEND"
            color = "\033[33m"  # Orange
        else:
            rating = "MANGELHAFT"
            color = "\033[91m"  # Red

        print(f"Durchschnittlicher Score: {color}{avg_score:.1f}/100\033[0m")
        print(f"Gesamtbewertung: {color}{rating}\033[0m")
        print()

        # Empfehlungen
        print("EMPFEHLUNGEN:")
        for baustein, data in bsi_results.items():
            if data['score'] < 70:
                print(f"  • {baustein}: Verbesserung benötigt (aktuell: {data['score']}/100)")

    def _save_json_report(self, bsi_results):
        """Speichert Report als JSON"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "project": "MoVi - Semantic Movie Search",
            "bsi_results": bsi_results,
            "summary": {
                "total_bausteine": len(bsi_results),
                "avg_score": sum(data['score'] for data in bsi_results.values()) / len(bsi_results)
            }
        }

        os.makedirs("backups", exist_ok=True)
        report_file = f"backups/bsi_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\n📄 Report gespeichert: {report_file}")
        print("=" * 60)


# Hauptprogramm
if __name__ == "__main__":
    tracker = BSIProgressTracker()
    tracker.generate_report()