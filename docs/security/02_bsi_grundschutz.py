# docs/security/02_bsi_grundschutz.py
"""
BSI IT-Grundschutz Kompendium - Zuordnung für MoVi
Generiert am: 05.01.2026
"""

BSI_MAPPING = {
    "APP.3.1": {
        "name": "Webanwendungen",
        "movi_bezug": "Django Backend Application",
        "maßnahmen": [
            {
                "id": "APP.3.1.A1",
                "beschreibung": "Sichere Programmierung",
                "AIContext.txt": "teilweise",
                "nachweis": "settings.py - CSRF_COOKIE_SECURE = False",
                "maßnahme": "CSRF_COOKIE_SECURE = True setzen"
            },
            {
                "id": "APP.3.1.A4",
                "beschreibung": "Input Validation",
                "AIContext.txt": "vorhanden",
                "nachweis": "test_movie_serializer.py - Validation Tests",
                "maßnahme": "Keine Änderung benötigt"
            }
        ]
    },
    "ORP.4": {
        "name": "Sicherheitsgateway",
        "movi_bezug": "API Gateway / CORS Konfiguration",
        "maßnahmen": [
            {
                "id": "ORP.4.A1",
                "beschreibung": "Zugriffskontrolle",
                "AIContext.txt": "fehlend",
                "nachweis": "CORS_ALLOW_ALL_ORIGINS = True",
                "maßnahme": "Auf Whitelist umstellen"
            }
        ]
    },
    "NET.1.1": {
        "name": "Netzplanung",
        "movi_bezug": "Docker Network Configuration",
        "maßnahmen": [
            {
                "id": "NET.1.1.A3",
                "beschreibung": "Netzwerksegmentierung",
                "AIContext.txt": "fehlend",
                "nachweis": "docker-compose.yml - Single Network",
                "maßnahme": "Frontend/Backend Netzwerke trennen"
            }
        ]
    },
    "CON.3": {
        "name": "Datensicherung",
        "movi_zerug": "PostgreSQL Backup",
        "maßnahmen": [
            {
                "id": "CON.3.A1",
                "beschreibung": "Regelmäßige Backups",
                "AIContext.txt": "fehlend",
                "nachweis": "Keine Backup-Skripte vorhanden",
                "maßnahme": "Docker Volume Backup implementieren"
            }
        ]
    }
}


def generate_report():
    """Generiert einen BSI-Status Report"""
    total_measures = 0
    implemented = 0
    partial = 0
    missing = 0

    for baustein, data in BSI_MAPPING.items():
        for maßnahme in data["maßnahmen"]:
            total_measures += 1
            if maßnahme["AIContext.txt"] == "vorhanden":
                implemented += 1
            elif maßnahme["AIContext.txt"] == "teilweise":
                partial += 1
            else:
                missing += 1

    print(f"BSI Grundschutz Analyse - MoVi")
    print(f"================================")
    print(f"Bausteine analysiert: {len(BSI_MAPPING)}")
    print(f"Maßnahmen insgesamt: {total_measures}")
    print(f"✓ Vollständig umgesetzt: {implemented}")
    print(f"⚠ Teilweise umgesetzt: {partial}")
    print(f"✗ Fehlend: {missing}")
    print(f"\nPriorität 1 (fehlend):")
    for baustein, data in BSI_MAPPING.items():
        for maßnahme in data["maßnahmen"]:
            if maßnahme["AIContext.txt"] == "fehlend":
                print(f"  - {baustein}.{maßnahme['id']}: {maßnahme['beschreibung']}")


if __name__ == "__main__":
    generate_report()