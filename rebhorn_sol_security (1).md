
# **Projektplan: MoVi - Semantische Filmsuche**
**Zeitraum:** 05.01.2026 – 08.01.2026  
**Analyse-Datum:** 29.12.2025  
**Code-Status:** Vollständige Backend-Infrastruktur mit Auth, Tests und CI

---

## **1. AKTUELLE ARCHITEKTUR-ANALYSE**

### **🔍 Erkannte Implementierungen:**

#### **✅ Vollständig implementiert:**
- **Microservices-Architektur:** 4 Docker-Container (PostgreSQL, Qdrant, Elasticsearch, Django)
- **Authentifizierung:** Session-basiert + CSRF-Schutz (`get-csrf/`, `check-auth/`)
- **API-Struktur:** 3 Haupt-App-URL-Konfigurationen
- **Testing:** 90%+ Coverage mit GitLab CI Pipeline
- **Sicherheitspakete:** Bandit, Ruff, Flake8 bereits integriert

#### **⚠️ Teilweise implementiert:**
- **User-Management:** Login/Register/Profile (Session-basiert)
- **Movie-API:** CRUD + Suche + Ähnlichkeitsfunktion
- **Favorites-System:** GET/POST/Check Endpoints

#### **❌ Fehlend (laut Anforderungen):**
- **Token-basierte Auth:** Kein JWT/OAuth2 für API-Zugriffe
- **API-Dokumentation:** Keine OpenAPI/Swagger Integration
- **Formelle UML-Dokumentation:** Keine Diagramme vorhanden
- **BSI-Grundschutz-Dokumentation:** Keine systematische Analyse
- **End-to-End Tests:** Keine Cypress/Frontend-Integration

---

## **2. ÜBERARBEITETER ARBEITSPLAN (akkurater)**

### **Tag 1: 05.01.2026 – Sicherheit & Dokumentation**

| Zeit | Aufgabe | Konkrete Änderungen | Code-Bezug |
|------|---------|-------------------|------------|
| **09:00-11:00** | **BSI-Grundschutz Analyse** | Zuordnung zu `docker-compose.yml` Services | NET.1.1 für Netzwerk |
| **11:00-13:00** | **UML-Diagramme** | Sequenzdiagramm für `movies/search/` | `urls (1).py` L8 |
| **13:00-15:00** | **OpenAPI-Spezifikation** | `drf-yasg` zu `requirements.txt` hinzufügen | Zeile 17 ergänzen |
| **15:00-17:00** | **Rate Limiting konfigurieren** | `REST_FRAMEWORK` in `settings.py` erweitern | Bestehende Konfig |

### **Tag 2: 06.01.2026 – API & Authentifizierung**

| Zeit | Aufgabe | Konkrete Änderungen | Code-Bezug |
|------|---------|-------------------|------------|
| **09:00-11:00** | **JWT-Authentifizierung** | `djangorestframework-simplejwt` installieren | `requirements.txt` +24 |
| **11:00-13:00** | **JWT-Endpoints** | `/api/token/` zu `users/urls.py` hinzufügen | `urls.py` L24+ |
| **13:00-15:00** | **API-Versionierung** | `api/v1/` Prefix zu Haupt-URLs | `urls (1).py` restrukturieren |
| **15:00-17:00** | **Auth-Tests erweitern** | JWT Tests zu bestehender Suite | `test_movie_views.py` pattern |

### **Tag 3: 07.01.2026 – Testing & CI**

| Zeit | Aufgabe | Konkrete Änderungen | Code-Bezug |
|------|---------|-------------------|------------|
| **09:00-11:00** | **Swagger Integration** | `drf_yasg` URLs zu Haupt-`urls.py` | Nach `admin/` hinzufügen |
| **11:00-13:00** | **Security Scanning** | Bandit in GitLab CI aktivieren | `.gitlab-ci.yml` L55 erweitern |
| **13:00-15:00** | **Coverage optimieren** | Gezielte Tests für Auth-Views | Von 90% → 91% |
| **15:00-17:00** | **Docker Security** | Netzwerk-Segmentierung in Compose | `docker-compose.yml` L63+ |

### **Tag 4: 08.01.2026 – Finalisierung**

| Zeit | Aufgabe | Konkrete Änderungen | Code-Bezug |
|------|---------|-------------------|------------|
| **09:00-11:00** | **Dokumentation erstellen** | `docs/` Ordner mit 5 MD-Dateien | Basierend auf vorhandenem Code |
| **11:00-13:00** | **Präsentation vorbereiten** | Live-Demo: Swagger + JWT Login | `localhost:8000/swagger/` |
| **13:00-15:00** | **Finale Tests** | Alle Tests in CI laufen lassen | `.gitlab-ci.yml` validieren |
| **15:00-17:00** | **Abnahme & Review** | Deliverables prüfen | Checkliste abhaken |

---

## **3. KONKRETE CODE-ÄNDERUNGEN (step-by-step)**

### **3.1 OpenAPI/Swagger Integration (Tag 1)**
```bash
# requirements.txt ergänzen (Zeile 18+):
drf-yasg==1.21.7
```

```python
# Haupt-urls.py (neben urls (1).py):
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="MoVi API",
        default_version='v1',
        description="Semantic Movie Search API - Existing Endpoints",
        contact=openapi.Contact(email="developer@movi.local"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger'),
    path('api/', include('movies.urls')),  # Ihre bestehenden URLs
    path('api/', include('users.urls')),
    path('api/', include('review.urls')),
]
```

### **3.2 JWT Authentifizierung (Tag 2)**
```bash
# requirements.txt ergänzen:
djangorestframework-simplejwt==5.3.0
```

```python
# settings.py (REST_FRAMEWORK ergänzen):
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # Neu
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Für Entwicklung
    ],
    'DEFAULT_THROTTLE_CLASSES': [  # Neu: BSI ORP.4
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    }
}

# Simple JWT Einstellungen:
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}
```

```python
# users/urls.py ergänzen (Zeile 30+):
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # ... bestehende URLs
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```

### **3.3 Docker Security (Tag 3)**
```yaml
# docker-compose.yml Netzwerk-Segmentierung (Zeile 63+):
networks:
  backend_network:
    driver: bridge
    internal: false  # Extern erreichbar
  frontend_network:
    driver: bridge

# Services anpassen:
services:
  db:
    networks:
      - backend_network
  web:
    networks:
      - backend_network
      - frontend_network
  vektor:
    networks:
      - backend_network
```

### **3.4 GitLab CI Security Scanning (Tag 3)**
```yaml
# .gitlab-ci.yml erweitern (nach Zeile 55):
security_scan:
  stage: test
  script:
    - echo "Running security scans..."
    - bandit -r . -x venv,tests -f json -o bandit-report.json
    - safety check --json --output safety-report.json
  artifacts:
    paths:
      - bandit-report.json
      - safety-report.json
    expire_in: 1 week
  allow_failure: true  # Nicht blockierend
```

---

## **4. UML-DIAGRAMME FÜR EXISTIERENDE ARCHITEKTUR**

### **Diagramm 1: System-Architektur (basierend auf docker-compose.yml)**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Django Web    │    │   PostgreSQL    │
│   (React)       │◄──►│   (Python)      │◄──►│   (db:5432)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
                               ▼
┌─────────────────┐    ┌─────────────────┐
│   Qdrant        │    │   Elasticsearch │
│   (vektor:6333) │    │   (elastic:9200)│
└─────────────────┘    └─────────────────┘
```

### **Diagramm 2: API-Endpoint Struktur (basierend auf urls.py)**
```
/api/
├── movies/                    # movies/urls.py
│   ├── GET/POST /            # MovieListCreateView
│   ├── GET /<id>/            # MovieDetailView
│   ├── GET /<id>/similar/    # MovieSimilarView
│   └── GET /search/          # MovieSearch
├── users/                    # users/urls.py
│   ├── POST /register/       # RegisterView
│   ├── POST /login/          # LoginView (Session)
│   ├── POST /token/          # JWT Token (neu)
│   └── GET /profile/         # ProfileView
└── review/                   # review/urls.py
    └── POST /movies/<id>/review/
```

### **Diagramm 3: Datenfluss - Movie Search**
```
          [Frontend]
              │ GET /api/movies/search?q=space
              ▼
          [Django View]
              │ 1. Text-Suche (Elasticsearch)
              │ 2. Vektor-Suche (Qdrant)
              │ 3. Ergebnisse kombinieren
              ▼
          [JSON Response]
```

---

## **5. BSI-GRUNDSCHUTZ ZUORDNUNG (konkret)**

### **Baustein APP.3.1 - Webanwendungen:**
- **Vorhanden:** Django CSRF, Input Validation in Serializern
- **Ergänzung:** Rate Limiting in `settings.py` (Tag 2)

### **Baustein ORP.4 - Sicherheitsgateway:**
- **Vorhanden:** CORS Konfiguration in `settings.py`
- **Ergänzung:** Netzwerk-Segmentierung in `docker-compose.yml` (Tag 3)

### **Baustein NET.1.1 - Netzwerkplanung:**
- **Vorhanden:** Docker Network `django_network`
- **Ergänzung:** Frontend/Backend Trennung (Tag 3)

### **Baustein CON.3 - Datensicherung:**
- **Vorhanden:** Docker Volumes für PostgreSQL, Elasticsearch, Qdrant
- **Ergänzung:** Backup-Skript dokumentieren (Tag 4)

---

## **6. TEST-ERWEITERUNG (basierend auf vorhandenen Tests)**

### **Vorhandene Test-Struktur:**
```bash
tests/
├── embedding_tests.py      # Schwere Embedding-Tests
├── test_embedding.py       # Mock-basierte Tests
├── test_movie_model.py     # Model-Tests
├── test_movie_search.py    # Search-Tests
├── test_movie_serializer.py # Serializer-Tests
├── test_movie_views.py     # View-Tests
├── test_vectors.py         # Vector-Service Tests
└── vector_tests.py         # Integrationstests
```

### **Neue Tests für SOL:**
```python
# tests/security/test_jwt_auth.py
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

class JWTAuthTests(APITestCase):
    def test_jwt_token_obtain(self):
        # Setup basierend auf test_movie_views.py Pattern
        user = User.objects.create_user('test', 'test@test.com', 'testpass123')
        
        response = self.client.post('/api/users/token/', {
            'username': 'test',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

# tests/api/test_rate_limiting.py
from rest_framework.test import APITestCase

class RateLimitingTests(APITestCase):
    def test_login_rate_limit(self):
        # 6 schnelle Login-Versuche
        for i in range(6):
            response = self.client.post('/api/users/login/', {
                'username': f'test{i}',
                'password': 'wrong'
            })
        
        self.assertEqual(response.status_code, 429)  # Too Many Requests
```

---

## **7. RISIKOANALYSE (basierend auf Codebase)**

### **Niedrige Risiken:**
- ✅ **Testing:** 90% Coverage vorhanden
- ✅ **CI/CD:** GitLab CI funktioniert
- ✅ **Docker:** Alle Services laufen stabil

### **Mittlere Risiken:**
- ⚠️ **Auth-Komplexität:** Session + JWT parallel betreiben
- ⚠️ **Time Management:** 4 Tage für alle Erweiterungen
- ⚠️ **Dokumentation:** Zeitaufwand unterschätzt

### **Kritische Abhängigkeiten:**
1. **Python Pakete:** `drf-yasg`, `djangorestframework-simplejwt` müssen kompatibel sein
2. **Django Version:** 4.2.7 - alle Erweiterungen müssen unterstützen
3. **Docker Netzwerk:** Änderungen dürfen bestehende Kommunikation nicht brechen

---

## **8. ABNAHMEKRITERIEN (konkret messbar)**

### **Technische Deliverables:**
- [ ] **Swagger UI:** Erreichbar unter `http://localhost:8000/swagger/`
- [ ] **JWT Endpoints:** `POST /api/users/token/` gibt `access` und `refresh` Token
- [ ] **Rate Limiting:** 6 Login-Versuche/Stunde → HTTP 429
- [ ] **UML Diagramme:** 3 PNG/PDF in `docs/uml/`
- [ ] **BSI-Dokument:** `docs/bsi_grundschutz.md` mit 4 Bausteinen
- [ ] **Test Coverage:** ≥90% (bestehender Stand gehalten)
- [ ] **CI Pipeline:** Erfolgreicher Run mit Security Scanning

### **Dokumentation:**
- [ ] `README.md` mit Updated Setup Instructions
- [ ] `docs/api/` mit OpenAPI Spec
- [ ] `docs/security/` mit BSI Analysis
- [ ] `docs/architecture/` mit UML Diagrams

---

## **9. ZEITOPTIMIERUNG (basierend auf Code-Analyse)**

### **Zeitersparnisse durch vorhandenen Code:**
1. **Testing:** Keine neue Test-Infrastruktur nötig → **2h gespart**
2. **Docker:** Bereits vollständig konfiguriert → **3h gespart**  
3. **Auth-Grundlage:** Session Auth existiert → **1h gespart**
4. **CI/CD:** GitLab CI läuft → **2h gespart**

### **Zeitintensive Aufgaben:**
1. **JWT Integration:** 2h (Komplexität: mittel)
2. **Swagger Setup:** 1,5h (Komplexität: niedrig)
3. **UML-Diagramme:** 2h (Komplexität: niedrig)
4. **BSI-Dokumentation:** 2h (Komplexität: mittel)

---

## **10. NOTFALLPLAN**

### **Wenn JWT zu komplex:**
- Fallback: Nur Swagger + Rate Limiting implementieren
- Dokumentation: JWT als "geplant" markieren

### **Wenn Zeit knapp:**
- Priorität 1: Swagger + Dokumentation
- Priorität 2: Rate Limiting
- Priorität 3: JWT (falls Zeit)

### **Wenn Tests brechen:**
- Bestehende Tests sichern (`git stash`)
- Neue Features isoliert testen
- Alte Funktionalität nicht verändern

---
