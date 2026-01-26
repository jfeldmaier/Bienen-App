# BeeHiveTracker Production Deployment

Anleitung für das Deployment von BeeHiveTracker auf einem Linux-Server mit Gunicorn, Systemd und optionalem Cloudflare Tunnel.

---

## 📋 Voraussetzungen

- Linux-Server (Ubuntu 20.04+ / Debian 11+ empfohlen)
- Python 3.9+
- Sudo-Rechte für Systemd-Service-Installation
- (Optional) Cloudflare-Account für Tunnel

---

## 🚀 Schritt 1: Server-Vorbereitung

### 1.1 System-Pakete installieren
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
```

### 1.2 Log-Verzeichnisse erstellen
```bash
sudo mkdir -p /var/log/beehivetracker
sudo chown $USER:www-data /var/log/beehivetracker
sudo chmod 775 /var/log/beehivetracker
```

### 1.3 Projektverzeichnis einrichten
```bash
cd ~
git clone https://github.com/yourusername/BeeHiveTracker.git
cd BeeHiveTracker
```

---

## 🔧 Schritt 2: Python-Umgebung einrichten

### 2.1 Virtual Environment aktivieren (falls vorhanden)
```bash
source bin/activate
```

### 2.2 Dependencies installieren
```bash
pip install -r requirements.txt
```

### 2.3 Produktions-Konfiguration erstellen
```bash
cp .env.example .env
nano .env
```

**Wichtige Einstellungen in `.env`:**
```env
FLASK_ENV=production
DEBUG=False
SESSION_COOKIE_SECURE=True
DATABASE_PATH=/home/jos/BeeHiveTracker/var/app-instance
UPLOAD_FOLDER=/home/jos/BeeHiveTracker/var/uploads
LOG_FILE=/var/log/beehivetracker/app.log
ACCESS_LOG=/var/log/beehivetracker/access.log
ERROR_LOG=/var/log/beehivetracker/error.log
GUNICORN_WORKERS=4
```

### 2.4 Admin-User erstellen
```bash
# Erstelle default_user.txt aus Template
cp default_user.example.txt default_user.txt
nano default_user.txt  # Setze USERNAME und PASSWORD

# Initialisiere Admin-User
python setup_user.py
```

---

## ⚙️ Schritt 3: Systemd-Service einrichten

### 3.1 Service-Datei installieren
```bash
sudo cp beehivetracker.service /etc/systemd/system/
sudo systemctl daemon-reload
```

### 3.2 Service aktivieren und starten
```bash
# Service beim Boot automatisch starten
sudo systemctl enable beehivetracker

# Service starten
sudo systemctl start beehivetracker

# Status prüfen
sudo systemctl status beehivetracker
```

### 3.3 Logs überwachen
```bash
# Systemd-Logs (Service-Status)
sudo journalctl -u beehivetracker -f

# Application-Logs
tail -f /var/log/beehivetracker/app.log

# Access-Logs
tail -f /var/log/beehivetracker/access.log
```

---

## 🌐 Schritt 4: Cloudflare Tunnel Setup (Empfohlen)

Cloudflare Tunnel ermöglicht sicheren Zugriff auf die App ohne Port-Forwarding oder öffentliche IP.

### 4.1 Cloudflared installieren
```bash
# Debian/Ubuntu
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Oder via Package-Manager
curl -L https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-archive-keyring.gpg >/dev/null
echo "deb [signed-by=/usr/share/keyrings/cloudflare-archive-keyring.gpg] https://pkg.cloudflare.com/cloudflared $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/cloudflared.list
sudo apt update && sudo apt install cloudflared
```

### 4.2 Cloudflare authentifizieren
```bash
cloudflared tunnel login
```
Dies öffnet Browser zur Authentifizierung mit Cloudflare-Account.

### 4.3 Tunnel erstellen
```bash
# Tunnel erstellen
cloudflared tunnel create beehivetracker

# Tunnel-ID notieren (wird angezeigt)
```

### 4.4 Tunnel-Konfiguration
```bash
sudo nano ~/.cloudflared/config.yml
```

**Inhalt:**
```yaml
tunnel: <TUNNEL_ID>
credentials-file: /home/jos/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: bienen.yourdomain.com
    service: http://127.0.0.1:5000
  - service: http_status:404
```

### 4.5 DNS-Eintrag erstellen
```bash
cloudflared tunnel route dns beehivetracker bienen.yourdomain.com
```

### 4.6 Tunnel als Service installieren
```bash
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared

# Status prüfen
sudo systemctl status cloudflared
```

---

## 🔒 Schritt 5: Cloudflare Zero Trust (Optional)

Zusätzliche Sicherheitsebene mit E-Mail-basierter Authentifizierung.

### 5.1 Cloudflare Dashboard öffnen
1. Gehe zu: https://one.dash.cloudflare.com/
2. Navigiere zu **Access** → **Applications**

### 5.2 Application erstellen
- **Name:** BeeHiveTracker
- **Domain:** `bienen.yourdomain.com`
- **Type:** Self-hosted

### 5.3 Access Policy erstellen
**Policy Name:** Email-basierter Zugriff
- **Action:** Allow
- **Rule:** Emails ending in `@yourdomain.com`
- Oder spezifische E-Mail-Adressen

### 5.4 Testen
Besuche `https://bienen.yourdomain.com` - Cloudflare fordert E-Mail-Verifizierung.

---

## 🧪 Schritt 6: Deployment testen

### 6.1 Health-Check
```bash
curl http://127.0.0.1:5000/health
# Erwartete Antwort: {"status":"healthy","database":"connected"}
```

### 6.2 Lokaler Zugriff
```bash
# Lokal (auf dem Server)
curl http://127.0.0.1:5000/login

# Oder mit Browser auf Server
firefox http://localhost:5000
```

### 6.3 Externer Zugriff (via Cloudflare)
```bash
curl https://bienen.yourdomain.com/health
```

Öffne Browser: `https://bienen.yourdomain.com`

---

## 📊 Wartung & Management

### Service-Management
```bash
# Service neu starten
sudo systemctl restart beehivetracker

# Service stoppen
sudo systemctl stop beehivetracker

# Service-Status prüfen
sudo systemctl status beehivetracker

# Auto-Start deaktivieren
sudo systemctl disable beehivetracker
```

### Log-Rotation
```bash
sudo nano /etc/logrotate.d/beehivetracker
```

**Inhalt:**
```
/var/log/beehivetracker/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 jos www-data
    sharedscripts
    postrotate
        systemctl reload beehivetracker > /dev/null 2>&1 || true
    endscript
}
```

### Datenbank-Backup
```bash
#!/bin/bash
# backup-beehive.sh
BACKUP_DIR=/home/jos/backups
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)

# Alle User-Datenbanken sichern
cp /home/jos/BeeHiveTracker/var/app-instance/*.db $BACKUP_DIR/
tar -czf $BACKUP_DIR/beehive_backup_$DATE.tar.gz $BACKUP_DIR/*.db

# Alte Backups löschen (älter als 30 Tage)
find $BACKUP_DIR -name "beehive_backup_*.tar.gz" -mtime +30 -delete
```

**Cronjob einrichten (täglich 2 Uhr):**
```bash
crontab -e
# Füge hinzu:
0 2 * * * /home/jos/backup-beehive.sh
```

### Updates durchführen
```bash
cd /home/jos/BeeHiveTracker
git pull origin main
source bin/activate
pip install -r requirements.txt
sudo systemctl restart beehivetracker
```

---

## 🔒 Sicherheits-Checkliste

- [ ] `DEBUG=False` in `.env` gesetzt
- [ ] `SESSION_COOKIE_SECURE=True` aktiviert (mit HTTPS)
- [ ] Starkes Admin-Passwort in `default_user.txt` gesetzt
- [ ] Firewall konfiguriert (Port 5000 nur lokal erreichbar)
- [ ] Cloudflare Tunnel verwendet (kein Port-Forwarding nötig)
- [ ] Log-Dateien mit eingeschränkten Berechtigungen (640)
- [ ] Regelmäßige Backups eingerichtet
- [ ] SSL/TLS via Cloudflare aktiviert
- [ ] (Optional) Cloudflare Zero Trust Access aktiviert

---

## 🆘 Troubleshooting

### Service startet nicht
```bash
# Prüfe Logs
sudo journalctl -u beehivetracker -n 50

# Prüfe Gunicorn manuell
cd /home/jos/BeeHiveTracker
source bin/activate
gunicorn --bind 127.0.0.1:5000 app:app
```

### Port bereits in Verwendung
```bash
# Finde Prozess
sudo lsof -i :5000

# Stoppe alten Prozess
sudo systemctl stop beehivetracker
```

### Datenbankfehler
```bash
# Prüfe Berechtigungen
ls -la /home/jos/BeeHiveTracker/var/app-instance/

# Repariere wenn nötig
sudo chown -R jos:www-data /home/jos/BeeHiveTracker/var/
```

### Cloudflare Tunnel verbindet nicht
```bash
# Prüfe Tunnel-Status
sudo systemctl status cloudflared

# Tunnel-Logs
sudo journalctl -u cloudflared -f

# Teste Tunnel manuell
cloudflared tunnel run beehivetracker
```

---

## 📚 Weiterführende Dokumentation

- [Flask Deployment](https://flask.palletsprojects.com/en/latest/deploying/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Cloudflare Tunnel Docs](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Systemd Service Units](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

---

## 🤝 Support

Bei Fragen oder Problemen:
- GitHub Issues: https://github.com/yourusername/BeeHiveTracker/issues
- Logs prüfen: `/var/log/beehivetracker/`
