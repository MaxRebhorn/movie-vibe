
# MoVi – Ablaufspezifikationen (Use Case Ablaufbeschreibungen)

## UC01: Film anhand einer Stimmung finden

**Akteur**: Anonymer oder registrierter Nutzer  
**Kurzbeschreibung**: Nutzer möchte Filme finden, die zu einer bestimmten Stimmung passen.

**Ablauf**:
1. Der Nutzer öffnet die Startseite.
2. Der Nutzer gibt eine Stimmung ein (z. B. „melancholisch, ruhig, minimalistisch“).
3. Das System wandelt die Eingabe mithilfe eines NLP-Modells (Natural Language Processing) in einen Vektor um.
4. Das System vergleicht diesen Vektor mit allen vorhandenen Film-Vektoren (via Vektor-Datenbank).
5. Das System sortiert die Ergebnisse nach Ähnlichkeit.
6. Eine Liste ähnlicher Filme wird angezeigt.
7. Der Nutzer kann auf einen Film klicken, um Details anzuzeigen.
8. Optional: Der Nutzer kann weitere Filter setzen (Genre, Länge, Sprache, ...).

---

## UC02: Film beschreiben (taggen)

**Akteur**: Registrierter Nutzer  
**Kurzbeschreibung**: Nutzer beschreibt einen Film in eigenen Worten, um ihn auffindbar zu machen.

**Ablauf**:
1. Der Nutzer loggt sich ein.
2. Der Nutzer klickt auf „Film hinzufügen“.
3. Der Nutzer gibt Titel, ggf. Beschreibung, Bild und Link zum Film ein.
4. Der Nutzer beschreibt den Film in einem Freitextfeld mit Eindrücken, Stimmung, visueller Sprache, etc.
5. Das System erstellt ein Embedding (Vektor) aus dem Text.
6. Der Film samt Embedding wird gespeichert und ist durchsuchbar.
7. Der Nutzer erhält eine Bestätigung und kann den Film sofort aufrufen.

---

## UC03: Film bewerten und kommentieren

**Akteur**: Registrierter Nutzer  
**Kurzbeschreibung**: Nutzer möchte einem Film Feedback geben.

**Ablauf**:
1. Der Nutzer besucht eine Film-Detailseite.
2. Der Nutzer klickt auf „Bewerten“.
3. Der Nutzer vergibt eine Punktzahl (1–5 Sterne).
4. Optional: Der Nutzer schreibt einen Kommentar.
5. Das System speichert die Bewertung und aktualisiert den Bewertungsdurchschnitt.
6. Die Bewertung ist öffentlich sichtbar (Name, Punktzahl, Kommentar).

---

## UC04: Eigene Beschreibung mit anderen vergleichen

**Akteur**: Registrierter Nutzer  
**Kurzbeschreibung**: Nutzer möchte sehen, wie sein Eindruck von einem Film im Vergleich zu anderen steht.

**Ablauf**:
1. Der Nutzer ruft einen Film auf, den er selbst beschrieben hat.
2. Das System zeigt eine Vergleichsansicht:  
   - Nutzer-Embedding vs. Durchschnitts-Embedding  
   - Visualisierung: z. B. Radar-Chart, Punktwolke oder Ähnlichkeitswert
3. Nutzer kann sehen, wie stark seine Sichtweise von anderen abweicht oder übereinstimmt.

---

## UC05: Admin löscht problematische Inhalte

**Akteur**: Admin  
**Kurzbeschreibung**: Der Admin möchte Inhalte entfernen, die gegen die Richtlinien verstoßen.

**Ablauf**:
1. Admin meldet sich im Adminbereich an.
2. Admin sieht gemeldete Inhalte (z. B. toxische Kommentare, falsche Filmeinträge).
3. Admin klickt auf „Entfernen“ oder „Sperren“.
4. System löscht oder versteckt den Inhalt, ggf. mit Feedback an den User.
5. Admin kann optional den betroffenen Nutzer verwarnen oder sperren.

---

## UC06: Ähnliche Filme zu einem bestimmten Film anzeigen

**Akteur**: Anonymer oder registrierter Nutzer  
**Kurzbeschreibung**: Der Nutzer möchte Filme sehen, die einem bestimmten Film ähnlich sind.

**Ablauf**:
1. Der Nutzer ruft die Detailseite eines Films auf.
2. Das System ruft das Embedding (Vektor) dieses Films ab.
3. Das System sucht in der Vektor-Datenbank nach ähnlichen Embeddings.
4. Eine Liste ähnlicher Filme wird nach Ähnlichkeit sortiert angezeigt.
5. Der Nutzer kann sich durch die Vorschläge klicken und weitere Details anzeigen lassen.

Optional:
- Nutzer kann anpassen, **wonach** die Ähnlichkeit priorisiert werden soll (z. B. Stimmung, Handlung, visuelle Sprache).
