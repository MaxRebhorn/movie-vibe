# Pflichtenheft: MoVi – Semantische Filmsuche & Vibe-Matching

---

## 1. Einleitung

**Projektname:** MoVi  
**Projektziel:** Entwicklung eines voll funktionalen Web-Prototyps für eine semantische, vibe-basierte Filmempfehlungsplattform.  
**Auftraggeber:** AFBB  
**Entwickler:** Max Rebhorn  
**Abgabetermin:** 26.08.2025  

---

## 2. Zielsetzung

MoVi ermöglicht es Nutzern, Filme nicht nur nach Genre oder Schauspielern, sondern vor allem nach ihrer emotionalen Wirkung, visuellen Sprache und Stimmung ("Vibe") zu finden. Der Prototyp soll folgende Kernziele erfüllen:

- Intuitive, textbasierte Stimmungssuche
- Automatische Ähnlichkeitsempfehlungen auf Filmdetailseiten
- Community-getriebene Filmbeschreibungen und Bewertungen
- Moderne, skalierbare Architektur mit Django, React und Qdrant

---

## 3. Zielgruppe

- **Anonyme Nutzer:** Suchen und Filme ansehen, aber keine Bewertungen
- **Registrierte Nutzer:** Bewerten, taggen, Filme hinzufügen
- **Admins:** Moderation, Benutzerverwaltung, Inhaltsprüfung

---

## 4. Funktionale Anforderungen

### 4.1 Such- und Navigationsfunktionen

| Funktion | Beschreibung | Priorität |
|----------|--------------|-----------|
| Textsuche | Suche nach Titeln und Synopsis | Hoch |
| Filmdetailseite | Alle Infos + Ähnlichkeitsvorschläge | Hoch |
| Ähnlichkeitsempfehlung | 5 ähnliche Filme pro Detailseite (70% Stimmung, 30% Erzählstil) | Hoch |
| Filtern nach Genre, Jahr, Tags | Filterung von Suchergebnissen | Mittel |

### 4.2 Community-Features

| Funktion | Beschreibung | Priorität |
|----------|--------------|-----------|
| Manuelles Hinzufügen von Filmen | Nutzer können Filme eintragen | Hoch |
| TMDB-Import | Automatischer Datenabgleich mit manueller Bestätigung | Mittel |
| Dublettenprüfung | Weiterleitung bei bereits vorhandenen Filmen | Mittel |
| Bewertungen & Kommentare | Sternebewertung und Freitext | Hoch |
| Tagging | Nutzerdefinierte Stichworte für Filme | Mittel |

### 4.3 Benutzerverwaltung

| Funktion | Beschreibung | Priorität |
|----------|--------------|-----------|
| Registrierung/Login | JWT-basierte Authentifizierung | Hoch |
| Rollen: User/Admin | Unterschiedliche Berechtigungen | Hoch |
| Admin-Moderation | Löschen von Inhalten, Sperren von Nutzern | Mittel |

---

## 5. Nicht-funktionale Anforderungen

- **Performance:** Ladezeiten < 3 Sekunden für Suchanfragen und Ähnlichkeitsvorschläge
- **Usability:** Intuitive Bedienbarkeit, klare Navigation
- **Skalierbarkeit:** Modularer Aufbau, erweiterbare Datenbank- und Vektorsuche
- **Datenschutz:** Keine unnötige Speicherung personenbezogener Daten

---

## 6. Technische Spezifikation

### 6.1 Systemarchitektur

| Komponente | Technologie |
|------------|-------------|
| Frontend | React |
| Backend | Django + Django REST Framework |
| Datenbank | PostgreSQL |
| Vektorsuche | Qdrant (Docker) |
| Embeddings | SentenceTransformers (`all-MiniLM-L6-v2`) |
| Deployment | Docker Compose |

### 6.2 Datenmodelle (Auszug)

**Movie:**
- Titel, Synopsis, Jahr, Genre, Tags, Poster-URL, Embedding-Vektor

**Review:**
- User, Movie, Rating, Kommentar

**User:**
- Username, E-Mail, Passwort, Rolle (User/Admin)

### 6.3 API-Endpoints (Beispiele)

- `GET /movies/` – Filmliste
- `GET /movies/search/?q=...` – Textsuche
- `GET /movies/vibesearch/?q=...` – Semantische Suche
- `POST /movies/` – Film anlegen
- `GET /movies/{id}/similar/` – Ähnliche Filme

---

## 7. Abnahmekriterien

Der Prototyp gilt als abgenommen, wenn:

1. Alle Kernfunktionen aus Abschnitt 4 implementiert und fehlerfrei nutzbar sind.
2. Der Workflow **"Suche → Filmdetail → Ähnliche Filme"** vollständig umgesetzt ist.
3. Die technische Architektur dem vorgegebenen Stack entspricht.
4. Eine lauffähige Version mit Docker Compose bereitgestellt werden kann.
5. Testdaten und eine Demo der Hauptuse-cases vorliegen.

---

## 8. Projektplan (Meilensteine)

1. **MVP Backend** – Django mit Textsuche  
2. **Vektorsuche** – Qdrant-Integration  
3. **User-Features** – Login, Bewertungen, Tagging  
4. **Frontend** – React-Oberfläche  
5. **Deployment & Testing** – Docker, Abnahme

---

## 9. Risiken und Annahmen

- **Risiko:** Performance bei großen Embedding-Mengen  
  **Maßnahme:** Indexierung und Caching in Qdrant  
- **Annahme:** TMDB-API ist verfügbar und stabil  
- **Risiko:** Community-Akzeptanz des Tagging-Systems  
  **Maßnahme:** Gamification-Ansätze prüfen

---

## 10. Glossar

- **Vibe:** Emotionale Wirkung/Stimmung eines Films
- **Embedding:** Numerische Repräsentation von Text (Vektor)
- **Qdrant:** Vektordatenbank für semantische Suche
- **TMDB:** The Movie Database – externe Film-Datenquelle

---

**Dokumentversion:** 1.0  
**Stand:** 15.07.2025  
**Autor:** Max Rebhorn

---
