# Changelog - Bienen-App

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

---

## [2025-11-29] - UI-Verbesserungen Inspektionen-Übersicht & Mobile Navigation

### 🎨 UI/UX Verbesserungen

#### Vergrößerte Aktionsbuttons in Inspektionen-Übersicht
- **Bootstrap Icons eingebunden**: CDN-Link für Bootstrap Icons hinzugefügt in `base.html`
- **Größere Buttons**: 
  - `btn-sm` Klasse entfernt für mehr Sichtbarkeit
  - Padding erhöht von `0.25rem 0.5rem` auf `0.5rem 0.75rem`
  - Minimale Breite von 42px für einheitliche Größe
- **Gefüllte Icons**: 
  - Bearbeiten-Button: `bi-pencil-fill` (gefülltes Stift-Icon)
  - Löschen-Button: `bi-trash-fill` (gefülltes Mülleimer-Icon)
- Bessere Erkennbarkeit und Bedienbarkeit der Aktionsbuttons

#### Mobile Schnellzugriff auf Inspektionen
- **Neue Schaltfläche** neben dem Hamburger-Menü in mobiler Ansicht
- Direkter Zugriff auf Inspektionen-Übersicht ohne Menü öffnen zu müssen
- **Gelber Button** mit `bi-clipboard-check-fill` Icon
- Nur sichtbar in mobiler Ansicht (`d-lg-none`)
- Optimierte Navigation für häufig genutzten Bereich

### 🗂️ Geänderte Dateien

**Templates:**
- `templates/base.html` - Bootstrap Icons CDN eingebunden, Mobile Schnellzugriff-Button hinzugefügt
- `templates/inspektionen_liste.html` - Aktionsbuttons vergrößert, gefüllte Icons verwendet

---

## [2025-11-19] - Inkonsistenzen behoben & UI-Verbesserungen

### 🔧 Behobene Fehler

#### Feldnamen-Inkonsistenz
- **Problem**: Feld `brutbereich` in Forms vs. `brut` in Models führte zu Template-Fehlern
- **Gelöst**: 
  - `forms.py`: `brutbereich` → `brut` in `InspectionForm` und `BatchInspectionForm`
  - `app.py`: `request.form.get('brutbereich')` → `request.form.get('brut')` in Batch-Inspektion
  - `templates/inspektion_form.html`: Formular-Felder angepasst
  - `templates/batch_inspektion_form.html`: Formular-Felder angepasst

#### Sterne-Bewertung invertiert
- **Problem**: Sterne wurden invertiert angezeigt (Formular vs. Anzeige)
- **Gelöst**: CSS-Regel `flex-direction: row-reverse` nur für `.rating.editable` (Formulare), normale Darstellung für `.rating` (Anzeige)

#### TypeError bei leeren Bewertungen
- **Problem**: `TypeError: '<' not supported between instances of 'int' and 'NoneType'`
- **Gelöst**: Null-Prüfung `{% if insp.volksstaerke %}` vor Sterne-Darstellung in `inspektionen_liste.html`

#### Inspektionen-Liste leer
- **Problem**: Template verwendete Variable `inspektionen`, Route lieferte `inspektionen_by_day`
- **Gelöst**: Template angepasst für gruppierte Darstellung nach Datum

#### Checkbox-Funktion defekt
- **Problem**: JavaScript-Selektor `.inspection-checkbox` fand keine Elemente
- **Gelöst**: Selektor geändert zu `input[name="inspection_ids"]`

### ✨ Neue Features

#### Feld "Drohnenbrut geschnitten"
- Model `Inspection`: Feld `drohnenbrut_geschnitten` (Boolean) hinzugefügt
- Forms: BooleanField in `InspectionForm` und `BatchInspectionForm`
- Templates: Checkbox in allen Formularen, Badge-Anzeige in Detailansicht
- Backend: Verarbeitung in `neue_inspektion`, `inspektion_bearbeiten`, `batch_inspektion`

#### Inspektionen-Übersicht: Mehrfachauswahl & Löschen
- **Checkboxen** für jede Inspektion
- **Dynamischer Löschen-Button** erscheint bei Auswahl (zeigt Anzahl)
- **Sicherheitsabfrage** vor dem Löschen mehrerer Inspektionen
- **Batch-Löschen** über bestehende Route `/inspektionen/loeschen`

#### Klickbare Inspektionen
- Gesamte Inspektionszeile ist klickbar und öffnet Detailansicht
- Buttons und Checkboxen mit `event.stopPropagation()` geschützt
- Hover-Effekt für besseres visuelles Feedback

### 🎨 UI/UX Verbesserungen

#### Kompakte Inspektionen-Übersicht
- **Neues Layout**: Checkbox → Info → Thumbnail → Aktionen (vertikal)
- **Datum-Gruppierung**: Inspektionen nach Tag gruppiert mit Wochentag
- **Thumbnail-Integration**: 
  - Zeigt erstes Bild (60×60px) wenn vorhanden
  - Nur angezeigt bei vorhandenen Bildern (kein Platzhalter)
  - Klickbar zur Detailansicht
- **Kompakte Info-Zeile**:
  - Kleinere Sterne (0.75rem)
  - Mini-Badges (👑, 🔍, 🐝)
  - Honigertrag mit Emoji
  - Bilderzähler bei mehreren Fotos
- **Vertikale Aktions-Buttons**: Bearbeiten und Löschen untereinander statt nebeneinander
- **Text-Kürzung**: Notizen auf 500px begrenzt mit `text-truncate`

#### CSS-Verbesserungen
- `.rating.editable` für Formulare (mit `flex-direction: row-reverse`)
- `.rating` für Anzeige (normale Reihenfolge)
- Hover-Effekte für List-Items
- Kompakte Badge-Stile

### 📚 Dokumentation

#### README.md
- Features-Sektion erweitert mit allen Bewertungskriterien
- Projektstruktur aktualisiert (`InspectionImage` Model, drei Forms)
- Template-Liste mit Beschreibungen
- Datenbankmodell-Dokumentation mit allen Feldern

#### migrations/README
- Key Components mit allen Routen und Modellen aktualisiert
- Wichtige Patterns erweitert:
  - Klarstellung `brut` (nicht `brutbereich`)
  - `BatchInspectionForm.colony_ids.choices` Muster
  - Cascade-Delete für Images
  - Star-Rating CSS-Klassen

#### project_structure.txt
- Vollständige Verzeichnisstruktur
- Alle Template-Dateien aufgelistet
- Aktuelle Dependency-Versionen
- `var/` Struktur mit DB und Uploads

### 🗂️ Geänderte Dateien

**Backend:**
- `forms.py` - Feldnamen harmonisiert, `drohnenbrut_geschnitten` hinzugefügt
- `app.py` - Batch-Inspektion korrigiert, `drohnenbrut_geschnitten` Verarbeitung

**Templates:**
- `templates/inspektionen_liste.html` - Komplettes Redesign mit Checkboxen, Thumbnails, kompaktem Layout
- `templates/inspektion_form.html` - Feldnamen korrigiert, `drohnenbrut_geschnitten` Checkbox
- `templates/batch_inspektion_form.html` - Feldnamen korrigiert, `drohnenbrut_geschnitten` Checkbox
- `templates/inspektion_detail.html` - `drohnenbrut_geschnitten` Badge-Anzeige

**Styling:**
- `static/styles.css` - `.rating.editable` vs `.rating`, kompakte Inspektionsliste

**Dokumentation:**
- `README.md` - Vollständig aktualisiert
- `migrations/README` - Patterns und Konventionen aktualisiert
- `project_structure.txt` - Komplette Struktur dokumentiert

---

## Legende
- 🔧 Bugfix
- ✨ Neues Feature
- 🎨 UI/UX Verbesserung
- 📚 Dokumentation
- 🗂️ Dateiänderungen
