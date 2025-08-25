
---

## Lastenheft für das Projekt "MoVi"

**Projektname:** MoVi – Semantische Filmsuche & Vibe-Matching
**Projektziel:** Entwicklung eines prototypischen, voll funktionalen Web-Prototyps für eine vibe-basierte Filmempfehlungsplattform.
**Auftraggeber:** AFBB
**Auftragnehmer:** Max Rebhorn
**Abgabetermin:** 26.08.2025

### 1. Einleitung und Zielsetzung

MoVi ist eine semantische Plattform zur Filmsuche und -empfehlung. Im Gegensatz zu klassischen Suchmaschinen ermöglicht MoVi Nutzern, Filme basierend auf ihrer emotionalen Wirkung, visuellen Sprache und Stimmung ("Vibe") zu finden. Das übergeordnete Ziel ist die Entwicklung eines funktionalen Prototyps, der die Kernfunktionalität demonstriert.

### 2. Zielgruppe

Die Plattform richtet sich primär an:
*   **Filmfans**, die neue Filme nach emotionaler Wirkung suchen.
*   **Nutzer**, die „Filme mit ähnlichem Vibe“ zu einem bekannten Film finden möchten.
*   **Creator oder Kuratoren**, die Filme beschreiben und taggen möchten.
*   **Moderatoren (Admins)**, die für die Datenqualität und -sicherheit der Plattform verantwortlich sind.

*(Quelle: Projektbeschreibung.md, Zielgruppen Beschreibungen.md)*

### 3. Funktionale Anforderungen (Kernfunktionen)

**a) Such- und Navigationsfunktionalität**
*   **Textbasierte Suche:** Einfache Suche nach Filmtiteln und Inhaltsangaben, um einen konkreten Film als Ausgangspunkt zu finden.
*   **Film-Detailseite:** Jeder Film verfügt über eine eigene Seite mit allen relevanten Informationen (Titel, Synopsis, Erscheinungsjahr, Genre, Tags, Poster, Community-Bewertungen).
*   **Ähnlichkeitsempfehlungen (Kernfeature):** **Ausschließlich auf der Detailseite eines Films** werden einem Nutzer automatisch bis zu 5 thematisch und stilistisch ähnliche Filme ("Ähnliche Vibes") vorgeschlagen. Die Ähnlichkeitsberechnung basiert auf einer Kombination aus Stimmung (70%) und Erzählstil (30%). Der Ähnlichkeitsgrad (z.B. "85%") ist klar gekennzeichnet.
*   **Filterfunktion für die Übersicht:** Nutzer können die *allgemeine* Filmliste oder Suchergebnisse nach Genre, Erscheinungsjahr, Tags, Mindestbewertung und verfügbarer Streaming-Plattform filtern, um einen Ausgangsfilm zu finden.

*(Quelle: Happy Path.md, User Stories.md - US01, US04, US05, Zielgruppen Beschreibungen.md - Hermann)*

**b) Datenverwaltung und Community-Features**
*   **Manuelles Hinzufügen von Filmen:** Nutzer können neue Filme zur Datenbank hinzufügen.
*   **Semi-automatischer Import:** Beim Hinzufügen eines Films wird automatisch die TMDB-Datenbank nach Basisdaten (Titel, Jahr, Regie, Synopsis) durchsucht und vorgeschlagen. Unklare Treffer müssen manuell bestätigt werden.
*   **Dublettenprüfung:** Versucht ein Nutzer, einen bereits existierenden Film hinzuzufügen, wird er stattdessen zur bestehenden Detailseite geleitet und kann dort eine Bewertung abgeben oder Tags ergänzen.
*   **Bewertungs- und Review-System:** Nutzer können Filme bewerten und kommentieren.
*   **Tagging-System:** Nutzer können Filme mit Schlagworten (Tags) versehen, die Stimmung und Vibe beschreiben.

*(Quelle: User Stories.md - US02, US03; Happy Path.md - Step 3; Zielgruppen Beschreibungen.md - Julia)*

**c) Benutzerverwaltung**
*   **Registrierung und Login:** Nutzer müssen sich registrieren und anmelden können, um Bewertungen abzugeben oder Filme hinzuzufügen (Authentifizierung via JWT).
*   **Berechtigungen:** Unterschiedliche Benutzerrollen (User, Admin) mit verschiedenen Rechten.
*   **Admin-Funktionen:** Admins können:
    *   Neu hinzugefügte Filme verifizieren oder ablehnen.
    *   Gemeldete Inhalte (Filme, Reviews, Kommentare) prüfen und löschen.
    *   Die Entscheidungsfindung erfolgt abgestuft (1-3 Admins je nach Schwere des Verstoßes).

*(Quelle: Zielgruppen Beschreibungen.md - Frank; User Stories.md - US06)*

### 4. Nicht-funktionale Anforderungen

*   **Benutzerfreundlichkeit:** Die Oberfläche muss intuitiv und selbsterklärend sein. Der Weg "Suche -> Filmdetail -> Ähnliche Filme" muss klar und einfach zu bedienen sein.
*   **Performance:** Suchergebnisse und insbesondere die Ähnlichkeitsempfehlungen auf der Detailseite müssen innerhalb weniger Sekunden geladen werden.
*   **Skalierbarkeit:** Die Architektur muss so gewählt sein, dass die Datenbank und die semantische Suche mit einer wachsenden Anzahl an Filmen und Nutzern umgehen kann.
*   **Datenschutz:** Es handelt sich um einen modernen, datenschutzfreundlichen Stack. Es werden keine personenbezogenen Daten unnötig gespeichert oder an Dritte verkauft.

*(Quelle: Projektbeschreibung.md)*

### 5. Technische Rahmenbedingungen (vom Auftraggeber vorgegeben)

Der Prototyp ist mit folgenden Technologien zu realisieren:
*   **Frontend:** React
*   **Backend:** Django (Django REST Framework)
*   **Datenbank:** PostgreSQL
*   **Vektorsuche/Semantic Search:** Qdrant (via Docker) - **Primär für die Generierung der Ähnlichkeitsempfehlungen**
*   **Embedding-Modell:** SentenceTransformers (`all-MiniLM-L6-v2`)
*   **Deployment:** Docker Compose

*(Quelle: Projektbeschreibung.md, Happy Path.md)*

### 6. Abnahmekriterien

Der Prototyp gilt als erfolgreich umgesetzt und abnahmefähig, wenn:
1.  Alle in Abschnitt 3 beschriebenen Kernfunktionen implementiert und funktional sind.
2.  **Der Workflow "Textsuche -> Auswahl eines Films -> Anzeige der Detailseite -> Anzeige einer Liste ähnlicher Filme" vollständig und fehlerfrei umgesetzt ist.**
3.  Die technische Implementierung dem in Abschnitt 5 beschriebenen Stack entspricht.
4.  Eine lauffähige Version via Docker Compose bereitgestellt werden kann.
5.  Die Funktionalität der wichtigsten Use-Cases (siehe `Zielgruppen Beschreibungen.md`) nachgewiesen werden kann (z.B. durch Testdaten und eine Demo).
