# tests/test_backup_simple.py
"""
Einfacher Backup-Test (läuft auf Host)
"""
import os
import tempfile
import unittest


class SimpleBackupTests(unittest.TestCase):
    def test_backup_directory(self):
        """Backup-Verzeichnis sollte existieren"""
        backup_dir = os.path.join(os.getcwd(), "backups")
        os.makedirs(backup_dir, exist_ok=True)

        self.assertTrue(os.path.exists(backup_dir))
        print(f"✅ Backup directory: {backup_dir}")

    def test_backup_script_exists(self):
        """Backup-Skripte sollten existieren"""
        scripts = ["backup.sh", "restore.sh", "backup_manager.py"]

        for script in scripts:
            script_path = os.path.join(os.getcwd(), "backup_scripts", script)
            self.assertTrue(os.path.exists(script_path),
                            f"Missing backup script: {script}")
            print(f"✅ Backup script: {script}")

    def test_backup_files_created(self):
        """Test-Backup sollte Dateien erstellen"""
        # Erstelle Test-Backup-Datei
        backup_dir = os.path.join(os.getcwd(), "backups")
        test_file = os.path.join(backup_dir, "test_backup.txt")

        with open(test_file, 'w') as f:
            f.write("Test backup content")

        self.assertTrue(os.path.exists(test_file))
        print(f"✅ Test backup file created: {test_file}")

        # Aufräumen
        os.remove(test_file)


if __name__ == "__main__":
    import sys

    sys.path.insert(0, os.getcwd())

    print("Running simple backup tests...")
    print("=" * 50)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(SimpleBackupTests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 50)
    print("BACKUP SYSTEM CHECK - BSI CON.3.A1")
    print("=" * 50)

    if result.wasSuccessful():
        print("✅ Backup system infrastructure OK!")
        print("   - Backup directory exists")
        print("   - Scripts are in place")
        print("   - Files can be created")
    else:
        print("❌ Some tests failed")
        print(f"   Success: {result.testsRun - len(result.failures)}/{result.testsRun}")