# BSI-Grundschutz Analyse für MoVi - Semantische Filmsuche

**Version:** 1.0  
**Datum:** 21.02.2026  
**Verantwortlich:** Max Rebhorn  
**Status:** Teilweise implementiert (69.5%)

---

## 1. Einleitung

Dieses Dokument beschreibt die Umsetzung der BSI-Grundschutz-Anforderungen für die MoVi-Plattform. Die Analyse basiert auf dem aktuellen Entwicklungsstand und identifiziert umgesetzte sowie noch ausstehende Sicherheitsmaßnahmen.

---

## 2. Übersicht der geprüften Bausteine

| Baustein | Bezeichnung | Status | Score |
|----------|-------------|--------|-------|
| NET.1.1 | Netzwerkmanagement | ⚠️ Teilweise | 66% |
| CON.3 | Datensicherung | ✅ Erfüllt | 87% |
| ORP.4 | Identitäts- und Berechtigungsmanagement | ⚠️ Teilweise | 75% |
| APP.3.1 | Webanwendungen | ⚠️ Teilweise | 50% |
| **Gesamt** | | | **69.5%** |

---

## 3. Detaillierte Baustein-Analyse

### 3.1 NET.1.1 - Netzwerkmanagement

**Ziel:** Sichere Netzwerkarchitektur und Segmentierung

#### Implementierte Maßnahmen:

| Prüfung | Status | Beschreibung |
|---------|--------|--------------|
| Docker Compose Konfiguration | ✅ | `docker-compose.yml` vorhanden mit definierten Netzwerken |
| Netzwerk-Segmentierung | ✅ | Backend/Frontend getrennt via `backend_network` und `frontend_network` |
| Web-Port-Exponierung | ✅ | Port 8000 nur für Frontend-Zugriff |
| Datenbank-Port-Sicherheit | ✅ | PostgreSQL nur auf localhost (127.0.0.1:5432) |

#### Verbesserungspotential:

| Prüfung | Status | Maßnahme |
|---------|--------|----------|
| Elasticsearch-Exponierung | ❌ | Port 9200 aktuell auf localhost exponiert - in Produktion nur intern binden |
| Qdrant-Exponierung | ❌ | Port 6333/6334 aktuell auf localhost exponiert - in Produktion nur intern binden |

**Empfehlung:** Für Produktionsbetrieb die Ports in `docker-compose.yml` auskommentieren oder auf interne Netzwerke beschränken.

---

### 3.2 CON.3 - Datensicherung

**Ziel:** Regelmäßige, gesicherte Backups

#### Implementierte Maßnahmen:

| Prüfung | Status | Beschreibung |
|---------|--------|--------------|
| Backup-Verzeichnis | ✅ | `backups/` existiert und ist gemountet |
| Backup-Skripte | ✅ | `backup_scripts/` mit vollständiger Toolchain |
| Backup-Skript | ✅ | `backup_manager.py` für automatisierte Backups |
| Restore-Skript | ✅ | `restore.py` für Wiederherstellung |
| Backup-Dateien | ✅ | 6 aktuelle Backup-Dateien vorhanden |
| Cron-Job | ✅ | Automatische tägliche Backups konfiguriert |

#### Backup-Konfiguration:

```bash
# Tägliches Backup um 02:00 Uhr
0 2 * * * cd /home/mrebhorn/projectsPython/movie-vibe && python3 backup_scripts/backup_manager.py >> backups/backup.log 2>&1




**Dokumentierte Wiederherstellung:**
```bash
# Backup einspielen
python3 backup_scripts/restore.py --backup-file backups/backup_20260221_020001.tar.gz
```

---

### 3.3 ORP.4 - Identitäts- und Berechtigungsmanagement

**Ziel:** Sichere Authentifizierung und Zugriffskontrolle

#### Implementierte Maßnahmen:

| Prüfung | Status | Beschreibung |
|---------|--------|--------------|
| CORS-Konfiguration | ✅ | Beschränkte Origins für Frontend |
| CSRF-Schutz | ✅ | Aktiv mit `CsrfViewMiddleware` |
| JWT-Authentifizierung | ✅ | Token-basierte API-Authentifizierung |
| Session-Authentifizierung | ✅ | Für Web-Interface |

#### Aktuelle Konfiguration:

```python
# CORS Settings
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Nur True in Entwicklung
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://frontend:3000",
]

# REST Framework Auth
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ]
}
```

**Hinweis:** `CORS_ALLOW_ALL_ORIGINS` ist aktuell an `DEBUG` gekoppelt - in Produktion muss dies explizit auf `False` gesetzt werden.

---

### 3.4 APP.3.1 - Webanwendungssicherheit

**Ziel:** Absicherung der Webanwendung gegen Angriffe

#### Implementierte Maßnahmen:

| Prüfung | Status | Beschreibung |
|---------|--------|--------------|
| CSRF-Schutz | ✅ | Aktiv für alle State-ändernden Operationen |
| Rate Limiting | ✅ | Konfiguriert in `REST_FRAMEWORK` |
| Input-Validierung | ✅ | In Serializern implementiert |

#### Aktuelle Rate-Limits:

```python
'DEFAULT_THROTTLE_RATES': {
    'anon': '100/day',    # 100 Anfragen pro Tag für anonyme User
    'user': '1000/day'    # 1000 Anfragen pro Tag für authentifizierte User
}
```

#### Verbesserungspotential:

| Prüfung | Status | Maßnahme |
|---------|--------|----------|
| DEBUG-Modus in Produktion | ❌ | `DEBUG = False` muss in Produktion gesetzt werden |
| Session Cookie Secure | ❌ | `SESSION_COOKIE_SECURE = True` für HTTPS |
| HTTPS-Erzwingung | ❌ | `SECURE_SSL_REDIRECT = True` in Produktion |

**Empfehlungen für Produktions-Settings:**

```python
# In Produktion (production.py oder Umgebungsvariablen)
DEBUG = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 Jahr
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

---

## 4. Risikobewertung

### Aktuelle Risiken (Entwicklungsumgebung):

| Risiko | Wahrscheinlichkeit | Auswirkung | Maßnahme |
|--------|-------------------|------------|----------|
| Elasticsearch/Qdrant exponiert | Mittel | Hoch | Für Produktion Ports schließen |
| DEBUG-Modus aktiv | Gering (Dev) | Hoch | Umgebungsvariable für Produktion setzen |
| Kein HTTPS | Gering (Dev) | Mittel | In Produktion mit Reverse Proxy umsetzen |

### Akzeptierte Restrisiken:

- In der Entwicklungsumgebung werden Dienste lokal exponiert (bewusst für Entwicklung)
- Rate Limiting ist konservativ eingestellt (100/day für Anon) - kann bei Bedarf angepasst werden

---

## 5. Verantwortlichkeiten

| Rolle | Name | Kontakt |
|-------|------|---------|
| BSI-Beauftragter | Max Rebhorn | max.rebhorn@example.com |
| Entwicklungsleitung | Max Rebhorn | max.rebhorn@example.com |
| Betriebsverantwortung | Max Rebhorn | max.rebhorn@example.com |

---

## 6. Nächste Schritte

### Kurzfristig (vor Produktionsgang):

1. [ ] Elasticsearch-Ports in Produktion deaktivieren
2. [ ] Qdrant-Ports in Produktion deaktivieren  
3. [ ] DEBUG=False über Umgebungsvariable setzen
4. [ ] HTTPS mit Reverse Proxy konfigurieren
5. [ ] Session-Cookies auf Secure setzen

### Mittelfristig (Q2 2026):

1. [ ] Regelmäßige Penetrationstests etablieren
2. [ ] 2-Faktor-Authentifizierung implementieren
3. [ ] Audit-Logging für sicherheitsrelevante Events

### Langfristig (2026):

1. [ ] ISO 27001 Zertifizierung vorbereiten
2. [ ] Externes Security-Audit durchführen lassen

---

## 7. Änderungshistorie

| Datum | Version | Änderung | Autor |
|-------|---------|----------|-------|
| 21.02.2026 | 1.0 | Initiale Erstellung | Max Rebhorn |

---

## 8. Anhang

### Verwendete Prüfskripte

- `backup_scripts/bsi_progress.py` - Automatisierte BSI-Analyse
- `check_status.sh` - Fortschrittskontrolle

### Relevante Konfigurationsdateien

- `django_backend/settings.py` - Django-Sicherheitseinstellungen
- `docker-compose.yml` - Netzwerkkonfiguration
- `.gitlab-ci.yml` - CI/CD-Sicherheits-Scans
```
