
---

# MoVi – Flowcharts der Use Cases (Mermaid-Diagramme)

---

## UC01: Film anhand einer Stimmung finden

```mermaid
flowchart TD
    A[Start: Nutzer öffnet Startseite] --> B[Eingabe: Stimmungstext]
    B --> C[NLP-Modell erzeugt Vektor]
    C --> D[Vektorvergleich in der Vektor-Datenbank]
    D --> E[Sortierte Filmliste anzeigen]
    E --> F[Nutzer klickt auf Film-Detail]
    F --> G[Details anzeigen]
```

---

## UC02: Film beschreiben (taggen)

```mermaid
flowchart TD
    A[Start: Nutzer ist eingeloggt] --> B[Klickt auf Film hinzufügen]
    B --> C[Eingabe: Titel, Beschreibung, Link]
    C --> D[Eingabe: Freitext-Beschreibung – Vibe, Eindruck, usw.]
    D --> E[NLP-Modell erzeugt Embedding]
    E --> F[Film + Vektor speichern]
    F --> G[Bestätigung anzeigen]
```

---

## UC03: Film bewerten und kommentieren

```mermaid
flowchart TD
    A[Start: Nutzer auf Filmseite] --> B[Klickt auf Bewerten]
    B --> C[Gibt Sternebewertung ab]
    C --> D[Optional: Kommentar hinzufügen]
    D --> E[Speichern in Datenbank]
    E --> F[Durchschnitt aktualisieren]
    F --> G[Bewertung sichtbar machen]
```

---

## UC04: Eigene Beschreibung mit anderen vergleichen

```mermaid
flowchart TD
    A[Start: Nutzer auf eigenem Film] --> B[Vergleichsansicht öffnen]
    B --> C[Lade Nutzer-Embedding]
    C --> D[Lade Durchschnitts-Embedding]
    D --> E[Visualisiere Ähnlichkeit – z. B. Punktwolke]
    E --> F[Abweichung oder Übereinstimmung anzeigen]
```

---

## UC05: Admin löscht problematische Inhalte

```mermaid
flowchart TD
    A[Start: Admin loggt sich ein] --> B[Sieht gemeldete Inhalte]
    B --> C[Klickt auf Entfernen oder Sperren]
    C --> D[System löscht oder versteckt Inhalt]
    D --> E[Optional: Nutzer verwarnen]
```

---

## UC06: Ähnliche Filme zu einem bestimmten Film anzeigen

```mermaid
flowchart TD
    A[Start: Nutzer öffnet Film-Detailseite] --> B[Lade Embedding des Films]
    B --> C[Suche nach ähnlichen Embeddings]
    C --> D[Ergebnisse sortieren]
    D --> E[Ähnliche Filme anzeigen]
    E --> F[Nutzer klickt auf weiteren Film]
    F --> G[Details anzeigen]
```




