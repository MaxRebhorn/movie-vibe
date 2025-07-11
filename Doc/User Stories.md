Hier sind **realistische User Stories**, die technische Machbarkeit und praktische Nutzererfahrungen abbilden – ohne absolute Versprechungen:

---

### **US01: Kontextuelle Filmpersönlichkeits-Empfehlungen**  
**Als:** Nutzer, der einen bestimmten Film mag  
**Möchte ich:** die thematisch ähnlichsten verfügbaren Filme sehen  
**Damit:** ich passende Alternativen entdecke, wenn direkte "Wie X"-Vergleiche schwer sind  
*Akzeptanzkriterien:*  
1. Max. 5 Vorschläge basierend auf kombinierter Ähnlichkeit (Stimmung 70%, Erzählstil 30%)  
2. Klare Kennzeichnung: "Ähnlichkeitsgrad: 85%"  
3. Fallback: "Keine starken Treffer? Erweitere deine Filter" bei <3 Ergebnissen  

---

### **US02: Semi-automatisches Filmeintragen**  
**Als:** Nutzer, der einen Nischenfilm hinzufügen möchte  
**Möchte ich:** Basisdaten via TMDB importieren, aber manuelle Korrekturen vornehmen  
**Damit:** unbekannte Filme trotz unvollständiger APIs integriert werden  
*Akzeptanzkriterien:*  
1. Automatischer TMDB-Lookup bei Titaleingabe  
2. Warnung bei unklaren Matches: "Gemeint: [Titel A] (2022) oder [Titel B] (2019)?"  
3. Möglichkeit, fehlende Felder (Studio, Laufzeit) manuell zu ergänzen  

---

### **US03: Progressive Dublettenbehandlung**  
**Als:** Nutzer, der einen existierenden Film eintragen will  
**Möchte ich:** zur Bewertung/Ergänzung geleitet werden  
**Damit:** Datenqualität durch Community-Wissen steigt  
*Akzeptanzkriterien:*  
1. Vorschlag: "Film existiert! Möchten Sie stattdessen...  
   a) Eine Bewertung abgeben  
   b) Tags ergänzen  
   c) Streaming-Links aktualisieren"  
2. Direktes Springen zum Filmprofil nach Auswahl  

---


### **US04: Abgestuftes Mood-Filtering**  
**Als:** Nutzer mit klaren Stimmungspräferenzen  
**Möchte ich:** zwischen schneller Komfort-Filterung und präziser Ausschlusslogik wählen können  
**Damit:** ich je nach Kontext optimale Ergebnisse erhalte  

*Akzeptanzkriterien:*  
1. **Zwei Filtermodi:**  
   - **Komfort-Modus:**  
     * Reduziert unerwünschte Genres/Stimmungen in der Sortierung (z.B. "Horror >5 Plätze nach hinten")  
     * Visualisierung durch "Vermeidet: Krieg, Düster"-Badge  
   - **Präzisions-Modus:**  
     * Hartes Ausschließen bestätigter Attribute ("Zeige keine Kriegsfilme")  
     * Klare Statistik: "42 Filme durch Ihre Ausschlüsse entfernt"  

2. Transparenz bei Limitationen:  
   - Warnhinweis bei expliziten Inhalten: *"Manche Szenen können algorithmisch nicht erkannt werden"*  
   - Option: "Trotzdem anzeigen"-Button bei <10 Ergebnissen  

3. Ergebnis-Hierarchie:  
   - Präzisionsmodus: Strikte Match-Priorität (Ähnlichkeit > Rating)  
   - Komfortmodus: Ausgewogene Mischung (Ähnlichkeit 60% + Community-Rating 40%)  

---

### **US05: Robust-adaptierbare Filterprofile**  
**Als:** Nutzer mit wiederkehrenden Suchprofilen  
**Möchte ich:** gespeicherte Filter entweder strikt oder flexibel anwenden  
**Damit:** ich bei Bedarf maximale Präzision erzwingen kann  

*Akzeptanzkriterien:*  
1. **Drei Anwendungsoptionen beim Laden:**  
   | Option | Beschreibung | Nutzungsszenario |  
   |--------|-------------|------------------|  
   | **Strikt** | Keine Relaxierung, ggf. 0 Ergebnisse | "Ich will nur exakt 80er Sci-Fi" |  
   | **Balanced (Default)** | Leichte Relaxierung bei <15 Treffern | Themenabend mit Qualitätsfokus |  
   | **Flexibel** | Aggressive Relaxierung | "Zeig mir irgendwas in Richtung..." |  

2. Transparente Relaxierungslogik:  
   - Automatische Erweiterung nur bei expliziter Zustimmung ("Ergebnisse knapp? [ ] Jahr 1975-1989 statt 1980s")  
   - Klare Kennzeichnung relaxierter Kriterien:  
     ```diff
     - Produktionsjahr: 1980-1989  
     + Produktionsjahr: 1978-1991 (erweitert)
     ```

3. Robustheitsgarantien:  
   - Bei "Strikt"-Modus: **Keine automatischen Änderungen** (auch bei 0 Ergebnissen)  
   - Harte Ausschlüsse bleiben immer aktiv: ❌ Kriegsfilme → **nie** in Ergebnissen  


---

### **US06: Abgestufte Admin-Entscheidungsfindung**  
**Als:** Moderator  
**Möchte ich:** Entscheidungen basierend auf verfügbaren Beweisen treffen  
**Damit:** die Plattformqualität pragmatisch gesichert wird  
*Akzeptanzkriterien:*  
1. Abstufungen bei Flags:  
   - ✅ Ausreichend Beweise (1 Admin)  
   - ⚠️ Grenzfall (2 Admins)  
   - ❌ Offensichtlicher Verstoß (3 Admins)  
2. Option: "Unklar, mehr Beweise benötigt" mit Rückfrage an Melder  

---

