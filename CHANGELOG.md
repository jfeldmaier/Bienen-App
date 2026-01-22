# Changelog - Bienen-App

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

---

## [2025-12-17] - User-Verwaltung und Authentifizierung (UPDATED)

### 🔐 Sicherheit & Authentifizierung

#### Datenbank-Verwaltung & Pfade
- **Zentrale Instance-Folder**: Alle Datenbank-Dateien in `var/app-instance/`
  - `users.db` - Zentrale User-Datenbank
  - `bienen.db` - Existierende Daten für Admin-User "<USERNAME>"
  - `bienen_{username}.db` - Pro-User Datenbanken für neue User
- **Absolute Pfade**: Konsistente Datenbankverbindungen unabhängig von CWD
- **Legacy-Support**: Bestehende `bienen.db` wird für jos automatisch verwendet

#### Vollständiges Login-System implementiert
- **Login-Pflicht**: Zugriff auf die Anwendung nur nach erfolgreicher Anmeldung
- **Sichere Passwort-Speicherung**: pbkdf2:sha256 Hashing mit Werkzeug
- **Session-Management**: 10-Tage-Sessions mit automatischer Verlängerung bei Aktivität
- **Rate-Limiting**: Schutz vor Brute-Force-Angriffen (10 Versuche/Minute)
- **Account-Sperre**: Nach 3 Fehlversuchen 30 Minuten gesperrt
- **Sicherer SECRET_KEY**: Automatisch generiert und persistent gespeichert

#### Passwort-Anforderungen
- Mindestens 10 Zeichen
- Mindestens ein Großbuchstabe
- Mindestens ein Kleinbuchstabe
- Mindestens eine Zahl
- Mindestens ein Sonderzeichen

#### Multi-User-Unterstützung
- **Separate Datenbanken**: Jeder User erhält eigene `bienen_{username}.db`
- **User-Datenbank**: Zentrale `users.db` für Authentifizierung
- **Dynamisches Laden**: Korrekte DB wird beim Login automatisch geladen
- **Admin-User**: Initiales Setup mit Admin-User via setup_user.py

### 👥 Benutzerverwaltung

#### Admin-Funktionen
- **User anlegen**: Neue Benutzer mit optionalen Admin-Rechten erstellen
- **User löschen**: Benutzer entfernen (DB wird archiviert mit _deleted Suffix)
- **User-Übersicht**: Liste aller Benutzer mit Status und Fehlversuchen
- **Admin-Berechtigung**: Mehrere Admins möglich
- **Admin-Interface**: Route `/admin/users` nur für Administratoren

#### UI-Anpassungen
- **Login-Seite**: Bootstrap 5 Design mit Gradient-Hintergrund
- **Navbar erweitert**: 
  - Anzeige des eingeloggten Users
  - Logout-Button
  - Admin-Link (nur für Admins sichtbar)
- **User-Verwaltung**: Übersichtliche Tabelle mit Aktions-Buttons

### 📦 Neue Abhängigkeiten
- `Flask-Login==0.6.3` - Session-Management
- `Flask-Limiter==3.5.0` - Rate-Limiting

### 🗂️ Neue Dateien
- `user_models.py` - User-Datenbankmodell
- `setup_user.py` - Initialisierungs-Script für Admin-User
- `templates/login.html` - Login-Formular
- `templates/admin_users.html` - User-Verwaltungsoberfläche
- `secret_key.txt` - Automatisch generierter SECRET_KEY (nicht im Git)
- `users.db` - User-Datenbank (nicht im Git)

### 🔄 Geänderte Dateien
- `app.py` - Login-System, User-Verwaltung, @login_required für alle Routen
- `forms.py` - LoginForm und UserCreateForm mit Validierung
- `templates/base.html` - Navbar mit User-Info und Logout
- `requirements.txt` - Flask-Login und Flask-Limiter hinzugefügt

### 📋 Setup-Anleitung
1. Neue Pakete installieren: `pip install -r requirements.txt`
2. App starten: `python app.py` (Datenbanken werden automatisch in var/app-instance erstellt)
3. Setup-Script ausführen: `python setup_user.py` (erstellt Admin-User mit Passwort)
4. **Passwort nach dem Login ändern!**

**Hinweis**: Die Datenbank-Dateien befinden sich automatisch in `var/app-instance/` (nicht im Projekt-Root).

### ⚠️ Breaking Changes
- **Migration erforderlich**: Bestehende `bienen.db` wird nach `bienen_jos.db` migriert
- **Login notwendig**: Kein Zugriff mehr ohne Authentifizierung
- **Produktions-Hinweise**: 
  - HTTPS verwenden (SESSION_COOKIE_SECURE aktivieren)
  - WSGI-Server statt Flask dev server
  - Reverse Proxy (nginx/Apache) empfohlen

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
