# docs/security/01_schutzbedarfsanalyse.md
# Schutzbedarfsanalyse - MoVi
**Dokument-ID:** SBA-MOVI-2026-01-05  
**Version:** 1.0  
**Erstellt:** 05.01.2026, 09:30  
**Verantwortlich:** Max Rebhorn  

## 1. Systemübersicht
- **System:** MoVi - Semantische Filmsuche
- **Technologie:** Django 4.2.7, PostgreSQL, Docker
- **Services:** 4 Container (Web, DB, Qdrant, Elasticsearch)

## 2. Identifizierte Assets
| Asset | Typ | Schutzbedarf | Begründung |
|-------|-----|-------------|------------|
| PostgreSQL Datenbank | Daten | Hoch | Enthält Nutzerdaten + Passwort-Hashes |
| Qdrant Vektordatenbank | Daten | Mittel | Semantische Embeddings (keine PII) |
| Django Session Cookies | Authentifizierung | Hoch | Login-Zustand der Nutzer |
| API Endpoints | Schnittstelle | Mittel | Öffentlich zugänglich |

## 3. Bedrohungsanalyse
### 3.1 Externe Bedrohungen
1. **Brute-Force Attacken** auf `/api/users/login/`
2. **SQL Injection** durch fehlerhafte API-Parameter
3. **Cross-Site Request Forgery (CSRF)** trotz Django-Schutz

### 3.2 Interne Schwachstellen
1. **docker-compose.yml**: Alle Services im gleichen Netzwerk
2. **DEBUG=True** in Produktion (in docker-compose.yml Zeile 50)
3. **Kein Rate Limiting** für Login-Endpoints

## 4. Schutzziele
| Schutzgut | Vertraulichkeit | Integrität | Verfügbarkeit |
|-----------|----------------|------------|---------------|
| Nutzerpasswörter | Hoch | Hoch | Mittel |
| Film-Metadaten | Niedrig | Mittel | Hoch |
| API-Zugriff | Mittel | Hoch | Hoch |

## 5. Maßnahmenempfehlungen
### Sofort (Tag 1-2):
1. **Rate Limiting** für Login-Endpoints implementieren
2. **DEBUG=False** für Production-Setup dokumentieren
3. **Network Segmentation** in Docker

### Mittelfristig:
4. **JWT Tokens** für API-Authentifizierung
5. **Input Validation** in allen Serializern
6. **Security Headers** (CSP, HSTS)

---
**Nächster Schritt:** BSI-Grundschutz Bausteine zuordnen (10:30 Uhr)