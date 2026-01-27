# Production Setup - Lokale Deployment-Dokumentation

Diese Datei dokumentiert die lokalen Produktions-Setup-Dateien, die **NICHT** ins öffentliche Repository gehören.

## 📁 Lokale Produktions-Dateien (gitignored)

### 1. **Umgebungskonfiguration**
```
.env                          # Produktive Umgebungsvariablen (GITIGNORED)
.env.example                  # Vorlage für .env (IM REPO)
```

**Was gehört in .env (lokal):**
```
FLASK_ENV=production
DEBUG=False
SECRET_KEY=<your-secret-key>
SESSION_COOKIE_SECURE=True
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
DATABASE_URL=sqlite:///var/app-instance/bienen_jos.db
LOG_FILE=/home/jos/BeeHiveTracker/var/logs/app.log
LOG_LEVEL=INFO
```

### 2. **Systemd Service Management**
```
beehivetracker.service       # Systemd Unit für Gunicorn (GITIGNORED)
                              # Location: /etc/systemd/system/
```

**Setup-Schritte:**
```bash
# Service kopieren
sudo cp beehivetracker.service /etc/systemd/system/

# Service registrieren und starten
sudo systemctl daemon-reload
sudo systemctl enable beehivetracker.service
sudo systemctl start beehivetracker.service
```

### 3. **Credentials & Secrets**
```
secret_key.txt                # Flask SECRET_KEY (GITIGNORED)
default_user.txt              # Standard Admin-Zugangsdaten (GITIGNORED)
default_user.example.txt      # Beispiel-Vorlage (IM REPO)
```

**Sicherheitshinweis:**
- Niemals in Git committen
- `.gitignore` schützt diese Dateien automatisch
- `secret_key.txt` wird von `init_admin.py` generiert

### 4. **Datenbanken**
```
var/app-instance/
  ├── bienen_jos.db           # Bee-Colony Datenbank (GITIGNORED)
  ├── bienen_*.db.old         # Backups (GITIGNORED)
  └── users.db                # Benutzerverwaltung (GITIGNORED)
```

### 5. **Logs & Monitoring**
```
var/logs/
  ├── app.log                 # Flask App-Logs (GITIGNORED)
  ├── gunicorn_access.log     # HTTP Request Logs (GITIGNORED)
  └── gunicorn_error.log      # Gunicorn Error Logs (GITIGNORED)
```

### 6. **Cloudflare Tunnel (zukünftig)**
```
.cloudflared/
  ├── cert.pem               # Cloudflare Authentifizierung (GITIGNORED)
  ├── config.yml             # Tunnel-Konfiguration (GITIGNORED)
  └── tunnel.json            # Tunnel-Credentials (GITIGNORED)
cloudflared.log               # Tunnel Logs (GITIGNORED)
```

## 🚀 Neustart auf Produktionsserver

1. **Repository klonen (ohne Produktions-Dateien):**
```bash
git clone <repository-url> /home/jos/BeeHiveTracker
cd /home/jos/BeeHiveTracker
```

2. **Virtuelle Umgebung erstellen:**
```bash
python3 -m venv .
source bin/activate
```

3. **Dependencies installieren:**
```bash
pip install -r requirements.txt
```

4. **Lokale Produktions-Dateien hinzufügen:**
```bash
# .env kopieren und anpassen
cp .env.example .env
nano .env  # Konfigurieren

# Systemd Service einstellen
sudo cp beehivetracker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable beehivetracker.service
```

5. **Admin-Benutzer initialisieren:**
```bash
python init_admin.py
# Folge den Anweisungen im Terminal
```

6. **Service starten:**
```bash
sudo systemctl start beehivetracker.service
sudo systemctl status beehivetracker.service
```

## 📋 Checkliste Produktions-Readiness

- [ ] `.env` mit Produktionswerten konfiguriert
- [ ] `beehivetracker.service` in `/etc/systemd/system/` installiert
- [ ] `secret_key.txt` generiert (via `init_admin.py`)
- [ ] Admin-Benutzer erstellt
- [ ] Datenbank initialisiert (`var/app-instance/`)
- [ ] Apache Reverse-Proxy konfiguriert
- [ ] Gunicorn Service läuft und ist auto-start enabled
- [ ] Logs funktionieren (`var/logs/`)
- [ ] Health-Check erreichbar (`/health`)
- [ ] CSRF-Token in Formularen vorhanden
- [ ] Security Headers aktiv (X-Frame-Options, CSP, etc.)

## 🔒 Sicherheits-Anforderungen

**WICHTIG: Diese Dateien niemals committen:**
- `.env` (Umgebungsvariablen)
- `secret_key.txt` (SECRET_KEY für Flask)
- `default_user.txt` (Admin-Credentials)
- `var/app-instance/*.db` (Produktionsdatenbanken)
- `var/logs/*` (Log-Dateien mit sensitiven Daten)
- `.cloudflared/` (Cloudflare Authentifizierung)

**Git prüfen:**
```bash
# Sicherstellen, dass diese Dateien NICHT getracked werden:
git ls-files | grep -E '(\.env$|secret_key|default_user|\.db$|\.cloudflared)'
# Sollte NICHTS zurückgeben (nur .env.example und Beispiel-Dateien)
```

## 📊 Repo-Struktur für Public

```
BeeHiveTracker (Public Repository)
├── .github/
│   ├── GIT_WORKFLOW.md              (Git Best Practices)
│   └── PRODUCTION_SETUP.md          (Diese Datei)
├── templates/                       (HTML Templates)
├── static/                          (CSS, JS)
├── app.py                           (Flask Main)
├── forms.py                         (WTForms)
├── models.py                        (SQLAlchemy)
├── user_models.py                   (User Management)
├── init_admin.py                    (Setup Script)
├── setup_user.py                    (User Setup)
├── upload_utils.py                  (Upload Handler)
├── requirements.txt                 (Dependencies)
├── .env.example                     (Env Template)
├── default_user.example.txt         (Example Credentials)
├── DEPLOYMENT.md                    (Deployment Guide)
├── CHANGELOG.md                     (Version History)
├── README.md                        (Dokumentation)
└── project_structure.txt            (Projekt-Übersicht)

.gitignored (Local Only):
├── .env                             (Production Config)
├── secret_key.txt                   (Flask Secret)
├── default_user.txt                 (Real Credentials)
├── beehivetracker.service           (Systemd Unit)
├── .github/copilot-instructions.md  (AI Agent Instructions - Private)
├── var/                             (Runtime Data)
│   ├── app-instance/                (Databases)
│   ├── logs/                        (Application Logs)
│   └── uploads/                     (User Uploads)
├── migrations/                      (DB Migrations - local)
├── .cloudflared/                    (Cloudflare Config)
└── bin/, lib/, include/ (venv)      (Virtual Environment)
```

## 🔄 Workflow für Entwicklung

**Öffentliche Änderungen (ins Repo):**
```bash
# App-Features, Fixes, Templates
git add app.py forms.py models.py templates/
git commit -m "Feature: ..."
git push origin main
```

**Lokale Produktions-Änderungen (gitignored):**
```bash
# .env, Secrets, Config
# Diese werden NICHT committed
nano .env
# Änderungen sind lokal und sicher
```

## 📝 Hinweise

- `.gitignore` ist bereits konfiguriert - alle sensitiven Dateien sind geschützt
- `git status` zeigt nur App-Code an (Produktions-Dateien sind unsichtbar)
- Neue Produktionsdateien sollten zu `.gitignore` hinzugefügt werden
- Regelmäßig `git ls-files` prüfen, um sicherzustellen, dass keine Secrets getracked werden

---

**Erstellt:** Januar 2026  
**Für:** BeeHiveTracker Production Deployment  
**Status:** ✅ Produktionsreif
