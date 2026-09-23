# Changelog - Bienen-App

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

---

## [2026-09-23] - Security: .gitignore gehärtet

### 🔒 Sicherheit
- **SQLite-Nebendateien** (`*.db-journal`, `*.db-wal`, `*.db-shm`, analog für `*.sqlite`) werden ignoriert – sie enthalten ebenfalls DB-Inhalte
- **Alle `.env`-Varianten** (`.env.*`, z. B. `.env.bak`) werden ignoriert, nur `.env.example` bleibt im Repo
- **Schlüssel-/Zertifikatsdateien** (`*.pem`, `*.key`) werden ignoriert
- `default_user.example.txt` aus `.gitignore` entfernt – die Vorlage ist öffentlich und war bereits getrackt

---

## [2026-05-20] - Feature: Standort-Autocomplete mit bekannten Standorten

### ✨ Neue Funktion
- **Standort-Autocomplete** beim Anlegen und Bearbeiten von Völkern
  - HTML5 `<datalist>`-Element zeigt alle bekannten Standorte als Dropdown-Vorschläge
  - Benutzer können einen bekannten Standort auswählen oder frei einen neuen eingeben
  - Standorte werden alphabetisch sortiert angezeigt
  - Implementierung: `app.py` (`neues_volk`, `volk_bearbeiten`), `templates/volk_form.html`

---

## [2026-05-19] - Bugfix: Bearbeiten-Funktion für Bienenvölker

### 🐛 Bugfixes
- **Bearbeiten-Schaltfläche repariert** (`/voelker` und `/volk/<id>`): Drei Ursachen behoben:
  1. `volk_form.html`: Zurück-Link verwendete `form._obj.id` (kein WTForms-Attribut) → ersetzt durch `volk.id`
  2. `app.py` (`volk_bearbeiten`): Template-Kontext fehlte `volk`-Objekt → wird jetzt übergeben
  3. `forms.py` (`BeeColonyForm`): `queen_color` SelectField ohne leere Option → WTForms 3.x `pre_validate()` schlug bei Völkern ohne Farbe still fehl → `validate_choice=False` + leere Option ergänzt
- **Feldwerte explizit gesetzt** in `volk_bearbeiten`: Leere Strings werden als `None` in die DB geschrieben (statt leerer String), konsistent mit `neues_volk`
- **Gunicorn-Neustart** nach Code-Änderungen (lief 2 Tage mit altem Code ohne `entstehungsart`-Feld)
- **Flash-Meldung** bei erfolgreichem Speichern ergänzt

---

## [2026-05-19] - Völkerverwaltung: Neues Volk & Entstehungsart

### 🐝 Neue Funktion
- **"Neues Volk"-Button** in der Völkerliste (`/voelker`) ergänzt — Direktzugang zum Anlegen eines neuen Bienenvolks
- **Entstehungsart** wird jetzt in der Völkerliste als eigene Spalte angezeigt (Schwarm, Ableger, Vereinigung, Kauf, Zucht, Sonstiges)
- **Entstehungsart** wird in der Volk-Detailansicht im Steckbrief angezeigt

---

## [2026-04-19] - Inspektionsliste: Beobachtungen vollständig anzeigen

### 🐝 UI-Verbesserung
- Freitext-Beobachtungen (`notes`) in der Inspektionsliste werden nun vollständig und mehrzeilig angezeigt (zuvor nach einer Zeile abgeschnitten)

---

## [2026-02-19] - Login- und Bild-Workflow Fixes

### 🔐 Login-Session
- Flask-Talisman respektiert nun `SESSION_COOKIE_SECURE` aus der `.env`
- CSP-Nonce-Requirement entfernt, damit bestehende Inline-Skripte funktionieren

### 🖼️ Bilder & Inspektionen
- Bildpfade auf Volk-Detailseite konsistent über Inspektionsdatum (`YYYYMMDD`)
- Bearbeitungsformular zeigt vorhandene Bilder und erlaubt Löschen per Button
- Neue AJAX-Route zum Löschen einzelner Inspektionsbilder (inkl. Dateisystem)
- Lösch-Button deaktiviert sich nach Klick, 404 liefert JSON statt HTML


## [2026-01-26] - Production-Deployment & Security-Hardening

### 🚀 Production-Ready Deployment

#### WSGI-Server & Process Management
- **Gunicorn**: Production WSGI-Server mit Multi-Worker-Support
  - Konfigurierbare Worker-Anzahl via Environment-Variable
  - Automatische Log-Rotation
  - Graceful Restart bei Updates
- **Systemd-Service**: Automatischer Start/Stop/Restart
  - Auto-Start beim Booten
  - Crash-Recovery mit automatischem Neustart
  - Process-Management via `systemctl`

#### Environment-basierte Konfiguration
- **python-dotenv**: `.env`-Datei-Support für alle Konfigurationen
- **Flexible Pfade**: Database, Uploads, Logs via Environment-Variables
- **DEBUG-Mode-Control**: Production vs Development via `FLASK_ENV`
- **`.env.example`**: Template-Datei für schnelles Setup

#### Security Headers & Hardening
- **Flask-Talisman**: Umfassende Security-Header-Middleware
  - `Strict-Transport-Security` (HSTS) - 1 Jahr Max-Age
  - `X-Frame-Options: DENY` - Clickjacking-Schutz
  - `X-Content-Type-Options: nosniff`
  - `X-XSS-Protection` aktiviert
  - `Content-Security-Policy` mit CSP-Nonces für Inline-Scripts
- **SESSION_COOKIE_SECURE**: Aktivierbar für HTTPS-Only-Sessions
- **HTTPS-Enforcement**: Vorbereitet für Reverse-Proxy-Setup

#### Production-Logging
- **Strukturiertes Logging**: INFO/WARNING/ERROR-Levels
- **File-Handler**: Rotating Log-Files (max 10MB, 10 Backups)
- **Access-Logs**: Separate Gunicorn-Access-Logs
- **Error-Logs**: Dedizierte Error-Log-Files
- **Log-Location**: Konfigurierbar via `LOG_FILE` Environment-Variable

#### Error-Handling
- **Custom Error-Handler**: 
  - 404: Benutzerfreundliche "Seite nicht gefunden"-Meldung
  - 500: Interner Server-Fehler mit automatischem DB-Rollback
- **Health-Check-Endpoint**: `/health` für Monitoring und Load-Balancer
  - Testet Datenbankverbindung
  - Gibt JSON-Status zurück (`healthy`/`unhealthy`)

### 🌐 Cloudflare Tunnel Integration

#### Zero-Trust Network Access
- **Cloudflared-Support**: Sichere Verbindung ohne Port-Forwarding
- **DEPLOYMENT.md**: Vollständige Schritt-für-Schritt-Anleitung
  - Cloudflare Tunnel Installation
  - Authentifizierung & Tunnel-Setup
  - DNS-Routing-Konfiguration
  - Systemd-Service für Cloudflared
- **Zero-Trust-Access**: Optional E-Mail-basierte Authentifizierung
- **HTTPS-Enforcement**: SSL/TLS via Cloudflare ohne lokales Zertifikat

### 📁 Neue Dateien

#### Konfiguration
- `.env.example` - Environment-Variable-Template mit allen Optionen
- `DEPLOYMENT.md` - Umfassende Deployment-Dokumentation

#### Service-Management
- `beehivetracker.service` - Systemd-Unit-File mit Gunicorn-Konfiguration

### 🔧 Geänderte Dateien

#### `app.py` - Production-Erweiterungen
- Environment-Variable-Support via `python-dotenv`
- Flask-Talisman Security-Headers-Middleware
- `SESSION_COOKIE_SECURE` konfigurierbar
- Production-Logging mit RotatingFileHandler
- Health-Check-Endpoint `/health`
- Custom Error-Handler (404, 500)
- DEBUG-Mode via `FLASK_ENV` Environment-Variable

#### `requirements.txt` - Neue Dependencies
```
gunicorn==21.2.0           # Production WSGI-Server
python-dotenv==1.0.0       # Environment-Variable-Support
Flask-Talisman==1.1.0      # Security-Headers-Middleware
```

#### `.gitignore` - Production-Ignorierung
- `.env` - Environment-Konfiguration
- `logs/` - Log-Verzeichnisse
- `/var/log/beehivetracker/` - System-Logs

### 🔒 Sicherheits-Features (Zusammenfassung)

✅ **Passwort-Security**: pbkdf2:sha256 Hashing, 10+ Zeichen, Komplexitätsanforderungen  
✅ **Account-Lockout**: 3 Fehlversuche = 30min Sperre  
✅ **Rate-Limiting**: 10 Login-Versuche/Minute, 200 Requests/Tag  
✅ **CSRF-Protection**: WTForms auf allen POST-Routen  
✅ **SQL-Injection-Schutz**: SQLAlchemy ORM  
✅ **File-Upload-Validation**: Whitelist, Größenlimit, Dateinamen-Sanitization  
✅ **Security-Headers**: HSTS, X-Frame-Options, CSP, X-XSS-Protection  
✅ **Session-Security**: httponly, samesite=Lax, secure (mit HTTPS)  
✅ **Secret-Key-Management**: Auto-generiert, file-basiert  
✅ **Production-Logging**: Strukturiert, rotierend, konfigurierbar  

### 📋 Deployment-Checkliste

1. ✅ `.env` aus `.env.example` erstellen und anpassen
2. ✅ `DEBUG=False` und `FLASK_ENV=production` setzen
3. ✅ `SESSION_COOKIE_SECURE=True` aktivieren (mit HTTPS)
4. ✅ Admin-User via `setup_user.py` erstellen
5. ✅ Dependencies installieren: `pip install -r requirements.txt`
6. ✅ Systemd-Service installieren und aktivieren
7. ✅ (Optional) Cloudflare Tunnel einrichten
8. ✅ Health-Check testen: `curl http://localhost:5000/health`

### ⚠️ Breaking Changes

- **Environment-Variables erforderlich**: `.env`-Datei muss aus `.env.example` erstellt werden
- **Production-Mode**: `DEBUG=True` standardmäßig deaktiviert in `.env.example`
- **Log-Pfade**: Neue Standard-Log-Locations `/var/log/beehivetracker/`

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
