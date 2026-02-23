
---

# 🔐 **SCHUTZBEDARFSANALYSE für MoVi**  
**Nach Vorlage: Johannes Lötze / AFBB**  
**Datum: 14.12.2025**

## 1. ZIELSETZUNG DER ANALYSE
Festlegung des angemessenen Schutzniveaus für die semantische Filmplattform "MoVi" gemäß DSGVO und IT-Sicherheitsstandards.

## 2. BESCHREIBUNG DER VERARBEITUNG
### 2.1 Verarbeitungstätigkeit
- Nutzerregistrierung und -authentifizierung
- Speicherung von Filmpräferenzen (Favoriten)
- Verarbeitung von Nutzerbewertungen und -kommentaren
- Semantische Filmanalyse durch Embedding-Vektoren

### 2.2 Verantwortliche Stelle
Max Rebhorn 

### 2.3 Eingesetzte Technik
- Django Backend mit PostgreSQL
- React Frontend
- Qdrant Vektor-Datenbank
- Docker-Container

## 3. ZU SCHÜTZENDE WERTE (Assets)
| Asset | Beschreibung | Besitzer | Wertigkeit (1-5) |
|-------|-------------|----------|------------------|
| **Nutzerdatenbank** | PostgreSQL mit personenbezogenen Daten | Projektbetreiber | 5 |
| **Passwort-Hashes** | Authentifizierungsdaten | Nutzer | 5 |
| **Session-Daten** | Login-Sessions | Nutzer | 4 |
| **Film-Embeddings** | Semantische Vektoren | System | 2 |
| **TMDB-API-Key** | Externer API-Zugang | Projektbetreiber | 3 |
| **Systemverfügbarkeit** | Plattform-Erreichbarkeit | Alle | 4 |

## 4. BEDROHUNGEN
### 4.1 Externe Bedrohungen
| Bedrohung | Wahrscheinlichkeit | Auswirkung |
|-----------|-------------------|------------|
| **Brute-Force-Angriff** auf Login | Mittel | Hoch |
| **SQL-Injection** | Niedrig (durch ORM) | Sehr Hoch |
| **Cross-Site-Scripting** (XSS) | Mittel | Hoch |
| **DDoS-Angriff** | Niedrig | Mittel |
| **API-Key-Missbrauch** | Mittel | Mittel |

### 4.2 Interne Bedrohungen
| Bedrohung | Wahrscheinlichkeit | Auswirkung |
|-----------|-------------------|------------|
| **Fehlkonfiguration** CORS | Hoch | Mittel |
| **Unverschlüsselte Passwörter** | Niedrig | Sehr Hoch |
| **Session-Fixation** | Mittel | Hoch |
| **Log-Daten-Exposition** | Mittel | Mittel |

## 5. SCHWACHSTELLEN
### 5.1 Technische Schwachstellen
1. **CORS_ALLOW_ALL_ORIGINS = True** in Entwicklung
2. **Kein Rate-Limiting** für Login-Endpoints
3. **Session-Cookies ohne Secure-Flag** in Entwicklung
4. **Keine 2-Faktor-Authentifizierung**

### 5.2 Organisatorische Schwachstellen
1. **Fehlende Datenschutzerklärung** auf Website
2. **Kein Löschkonzept** für Nutzerdaten
3. **Kein Notfallplan** bei Datenpannen

## 6. RISIKOBEWERTUNG
### Risikomatrix nach ISO 27005:

| Risiko | Eintrittswahrsch. | Schadenshöhe | Risikostufe | Maßnahmenpriorität |
|--------|-------------------|--------------|-------------|-------------------|
| **Passwort-Diebstahl** | Mittel | Sehr Hoch | Hoch | 1 |
| **Session-Hijacking** | Mittel | Hoch | Hoch | 1 |
| **XSS in Kommentaren** | Mittel | Mittel | Mittel | 2 |
| **API-Key-Leakage** | Niedrig | Mittel | Niedrig | 3 |
| **DDoS** | Niedrig | Mittel | Niedrig | 3 |

## 7. SCHUTZBEDARF
### 7.1 Schutzziele nach ISO 27001

| Schutzbedarf | Vertraulichkeit | Integrität | Verfügbarkeit | Verbindlichkeit |
|--------------|-----------------|------------|---------------|-----------------|
| **Nutzerpasswörter** | Hoch (C) | Hoch (I) | Mittel (A) | Hoch |
| **Persönliche Daten** | Hoch (C) | Mittel (I) | Mittel (A) | Mittel |
| **Bewertungen** | Mittel (C) | Hoch (I) | Hoch (A) | Hoch |
| **Film-Metadaten** | Niedrig (C) | Mittel (I) | Hoch (A) | Niedrig |

**Legende:**
- **C** = Confidentiality (Vertraulichkeit)
- **I** = Integrity (Integrität)
- **A** = Availability (Verfügbarkeit)

### 7.2 Rechtlicher Schutzbedarf
- **DSGVO Art. 32:** Technische Maßnahmen für personenbezogene Daten
- **DSGVO Art. 25:** Privacy by Design/Default
- **TMDB API Terms:** Lizenzierung von Filmplakaten
- **Urheberrecht:** Schutz der Film-Metadaten

## 8. SCHUTZMASSNAHMEN
### 8.1 Technische Maßnahmen (Umsetzung)

**SOFORT (Priorität 1):**
```python
# 1. CORS-Sicherheit
CORS_ALLOW_ALL_ORIGINS = False  # Nur in Prod
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://ihre-domain.de",
]

# 2. Session-Sicherheit
SESSION_COOKIE_SECURE = True  # HTTPS erforderlich
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True

# 3. Passwort-Policy
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 10}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
]
```

**KURZFRISTIG (Priorität 2):**
- Rate-Limiting für `/api/login/` (max 5 Versuche/Stunde)
- Security Headers (CSP, X-Frame-Options)
- Logging von fehlgeschlagenen Logins

**MITTELFRISTIG (Priorität 3):**
- 2-Faktor-Authentifizierung (optional)
- Passwort-Reset-Funktion
- Datenexport (DSGVO Art. 20)

### 8.2 Organisatorische Maßnahmen
1. **Datenschutzerklärung** erstellen und verlinken
2. **Löschkonzept** für Nutzeraccounts dokumentieren
3. **Notfallplan** bei Datenpannen erstellen
4. **Regelmäßige Backups** (PostgreSQL + Qdrant)

## 9. RESTRISIKEN
Trotz Umsetzung aller Maßnahmen verbleibende Risiken:
1. **Zero-Day-Exploits** in Django oder React
2. **Social Engineering** (Phishing der Nutzer)
3. **Insider-Bedrohungen** (Admin-Account-Missbrauch)

## 10. ÜBERWACHUNG UND REVIEW
### 10.1 Monitoring
- **Wöchentlich:** Log-Review auf verdächtige Aktivitäten
- **Monatlich:** Update der Abhängigkeiten (pip/npm)
- **Quartalsweise:** Penetration-Test der Hauptfunktionen

### 10.2 Metriken
- Anzahl fehlgeschlagener Logins
- Response-Time der API-Endpoints
- Anzahl aktiver Nutzer/Favoriten

## 11. ANHANG

### A. Verwendete Abkürzungen
- **PII:** Personally Identifiable Information
- **CORS:** Cross-Origin Resource Sharing
- **XSS:** Cross-Site Scripting
- **DDoS:** Distributed Denial of Service

### B. Referenzen
- DSGVO Text: https://dsgvo-gesetz.de
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Django Security: https://docs.djangoproject.com/en/5.2/topics/security/

### C. Verantwortlichkeiten
| Rolle | Verantwortung | Kontakt             |
|-------|--------------|---------------------|
| Entwickler | Implementierung Sicherheitsmaßnahmen | Max Rebhorn         |
| Admin | Betrieb und Monitoring | Max Rebhorn         |
| Nutzer | Passwort-Sicherheit | Selbstverantwortung |

---

#