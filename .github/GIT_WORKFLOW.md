# Git Workflow für BeeHiveTracker

## 📋 Übersicht

Dieses Projekt teilt sich in zwei Teile:

1. **Öffentlicher App-Code** → ins GitHub Repository
2. **Lokale Produktions-Dateien** → bleiben nur lokal (gitignored)

## 🚀 Workflow: App-Features committen

### Wenn du an der App arbeitest (Features, Bugs, Templates):

```bash
# 1. Änderungen ansehen
git status

# 2. App-Code committen (diese Dateien werden automatisch erfasst)
git add app.py forms.py models.py templates/ static/
git commit -m "Feature: Neue Inspektions-Funktion hinzugefügt"

# 3. Ins Remote-Repo pushen
git push origin main
```

**Was wird committed:**
- ✅ `app.py`, `forms.py`, `models.py` (Python-Code)
- ✅ `templates/`, `static/` (Frontend)
- ✅ `README.md`, `CHANGELOG.md` (Dokumentation)
- ✅ `requirements.txt` (Dependencies)

**Was wird NICHT committed:**
- ❌ `.env` (Umgebungsvariablen)
- ❌ `secret_key.txt` (Flask Secret)
- ❌ `default_user.txt` (Admin-Credentials)
- ❌ Datenbanken (`*.db`)
- ❌ Logs
- ❌ `.cloudflared/` (Tunnel-Config)

---

## 🔒 Sicherheit: Lokale Produktions-Dateien

### Diese Dateien NIEMALS ins Repo!

```bash
# Sicherheitscheck - sollte NICHTS anzeigen:
git ls-files | grep -E '(\.env|secret_key|\.db|\.cloudflared)'

# Falls doch etwas getracked wird:
git rm --cached .env secret_key.txt
git commit -m "Remove: Sensitive files from git"
```

### Lokale Produktions-Dateien verwalten:

```bash
# .env lokal konfigurieren (wird nicht committed)
nano .env
git status  # Sollte .env NICHT zeigen

# Admin-User lokal erstellen
nano default_user.txt
python setup_user.py
git status  # Sollte default_user.txt NICHT zeigen
```

---

## 📝 Workflow: Änderungen dokumentieren

### CHANGELOG.md aktualisieren (WIRD ins Repo committed):

```bash
# Vor jedem Commit: CHANGELOG.md updaten
nano CHANGELOG.md

# Format:
# ## [1.2.0] - 2026-01-26
# ### Added
# - Neue Feature XYZ
# ### Fixed
# - Bug-Fix für ABC
# ### Changed
# - Verbesserung bei DEF

git add CHANGELOG.md
git commit -m "Update: CHANGELOG für Version 1.2.0"
```

---

## 🔄 Typischer Entwicklungs-Workflow

### 1. Feature entwickeln (lokal)
```bash
# Feature in app.py, models.py, templates/ hinzufügen
nano app.py
python app.py  # Testen

git status  # Nur App-Code sollte geändert sein
```

### 2. Tests (lokal)
```bash
# Auf http://127.0.0.1:5000 testen
# Admin-User mit credentials aus default_user.txt
```

### 3. Committen & Pushen
```bash
git add app.py forms.py models.py templates/ CHANGELOG.md
git commit -m "Feature: Beschreibung der Änderung"
git push origin main
```

### 4. Production-Config separat (bleibt lokal)
```bash
# .env nur lokal ändern
nano .env  # Keine Änderungen ins Repo!

# beehivetracker.service nur lokal updaten
nano beehivetracker.service  # Keine Änderungen ins Repo!
```

---

## 🎯 Checkliste vor Push

```bash
# 1. Git Status prüfen - nur App-Code sollte da sein
git status --short

# 2. Sensible Dateien checken (sollte leer sein)
git ls-files | grep -E '(\.env$|secret_key|\.db|cloudflared)'

# 3. CHANGELOG.md aktualisiert?
git diff CHANGELOG.md | head -20

# 4. Commits ansehen
git log --oneline -5

# 5. Pushen
git push origin main

# 6. GitHub: Pull Request erstellen & merge
```

---

## 🚨 Versehentlich gecheckt - Was tun?

Falls du versehentlich Secrets ins Repo gepusht hast:

```bash
# SOFORT Secrets aus der Geschichte entfernen:
git rm --cached .env secret_key.txt
git commit --amend -m "Remove: Sensitive files"
git push origin main --force-with-lease

# Von GitHub entfernen (wird cached):
# → Repository Settings → Delete Branch Cache

# Secrets ändern (da sie in Git-History sind):
# → Neue .env mit neuem SECRET_KEY erstellen
# → Benutzer-Passwörter zurücksetzen
```

---

## 📊 Repo-Status prüfen

```bash
# Alle getrackten Dateien anzeigen
git ls-files

# Nur gitignored Dateien anzeigen (lokal)
git status --short | grep "^??"

# Dateien die in .gitignore aber getracked sind (schlecht!)
git ls-files -o -i --exclude-standard

# Diff vor Push ansehen
git diff origin/main
```

---

## 💡 Tipps

### Separate Commits für verschiedene Änderungen:
```bash
# Feature in eigenem Commit
git add app.py forms.py
git commit -m "Feature: Neue Inspektions-Felder"

# Dokumentation in separatem Commit
git add README.md CHANGELOG.md
git commit -m "Docs: Update für neue Features"
```

### Nur bestimmte Dateien committen:
```bash
# Interactive staging
git add -p

# Dann nur die Teile auswählen die ins Repo sollen
```

### Lokale Änderungen von Remote-Änderungen trennen:
```bash
# Lokale .env Änderungen behalten, aber Remote pullen
git stash  # Lokale Änderungen speichern
git pull origin main  # Remote Code holen
git stash pop  # Lokale Änderungen zurück
```

---

## 📚 Dokumentation

- **Öffentliche Docs** (ins Repo): [README.md](README.md), [DEPLOYMENT.md](DEPLOYMENT.md)
- **Lokale Production-Docs** (nicht im Repo): [.github/PRODUCTION_SETUP.md](.github/PRODUCTION_SETUP.md)
- **Changelog** (ins Repo): [CHANGELOG.md](CHANGELOG.md)

---

## 🔐 Sicherheits-Checkliste

- [ ] `.env` mit echtem `SECRET_KEY` lokal
- [ ] `default_user.txt` mit echten Credentials lokal
- [ ] `secret_key.txt` generiert lokal
- [ ] Keine `.env.production` im Repo
- [ ] Keine Datenbanken (`*.db`) im Repo
- [ ] Keine Logs im Repo
- [ ] `.cloudflared/` nicht im Repo
- [ ] `git ls-files` zeigt keine sensitiven Dateien

---

**Erstellt:** Januar 2026  
**Für:** BeeHiveTracker  
**Status:** Production-Ready ✅
