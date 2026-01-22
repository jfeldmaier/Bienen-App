#!/usr/bin/env python3
"""
setup_user.py
-----------------------------
Einfaches Setup-Script für User-Verwaltung
Erstellt den Admin-User aus default_user.txt

Verwendung:
    python setup_user.py
"""

import os
import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime
import sys

def load_default_credentials():
    """Lädt Default-Credentials aus default_user.txt"""
    config_file = 'default_user.txt'
    if not os.path.exists(config_file):
        print("❌ Fehler: default_user.txt nicht gefunden!")
        print("Bitte erstellen Sie die Datei basierend auf default_user.example.txt")
        sys.exit(1)
    
    credentials = {}
    with open(config_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                credentials[key.strip()] = value.strip()
    
    if 'USERNAME' not in credentials or 'PASSWORD' not in credentials:
        print("❌ Fehler: USERNAME oder PASSWORD fehlt in default_user.txt")
        sys.exit(1)
    
    return credentials['USERNAME'], credentials['PASSWORD']

def setup_admin():
    """Erstellt User-Datenbank und Admin-User"""
    
    print("=" * 60)
    print("BeeHiveTracker - User-Setup")
    print("=" * 60)
    
    # Lade Credentials aus Datei
    admin_username, admin_password = load_default_credentials()
    print(f"\n🔐 Verwende Admin-User: {admin_username}")
    
    # 1. User-Datenbank erstellen
    print("\n📁 Erstelle User-Datenbank...")
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Users-Tabelle erstellen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            is_admin BOOLEAN NOT NULL DEFAULT 0,
            failed_login_attempts INTEGER NOT NULL DEFAULT 0,
            locked_until DATETIME,
            created_at DATETIME NOT NULL
        )
    ''')
    
    # Prüfe ob User bereits existiert
    cursor.execute('SELECT id FROM users WHERE username = ?', (admin_username,))
    existing = cursor.fetchone()
    
    if existing:
        print(f"⚠️  User '{admin_username}' existiert bereits!")
        response = input("Passwort zurücksetzen? (j/n): ")
        if response.lower() == 'j':
            password_hash = generate_password_hash(admin_password, method='pbkdf2:sha256')
            cursor.execute('''
                UPDATE users 
                SET password_hash = ?, is_admin = 1, failed_login_attempts = 0, locked_until = NULL
                WHERE username = ?
            ''', (password_hash, admin_username))
            conn.commit()
            print("✅ Admin-User aktualisiert")
        else:
            print("ℹ️  Keine Änderungen")
            conn.close()
            return
    else:
        # Admin-User erstellen
        print(f"\n👤 Erstelle Admin-User '{admin_username}'...")
        password_hash = generate_password_hash(admin_password, method='pbkdf2:sha256')
        cursor.execute('''
            INSERT INTO users (username, password_hash, is_admin, created_at)
            VALUES (?, ?, 1, ?)
        ''', (admin_username, password_hash, datetime.utcnow()))
        conn.commit()
        print("✅ Admin-User erstellt. Verwenden Sie setup_user.py mit entsprechenden Anweisungen.")
    
    conn.close()
    
    # 2. Datenbank-Migration
    print("\n📊 Datenbank-Migration...")
    
    # Nutze Admin-Username für DB-Namen
    db_filename = f'bienen_{admin_username}.db'
    
    if os.path.exists('bienen.db'):
        if os.path.exists(db_filename):
            print(f"⚠️  {db_filename} existiert bereits")
            response = input("Überschreiben mit bienen.db? (j/n): ")
            if response.lower() == 'j':
                import shutil
                backup = f"bienen_{admin_username}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                shutil.copy(db_filename, backup)
                print(f"✅ Backup: {backup}")
                shutil.copy('bienen.db', db_filename)
                print(f"✅ Migration: bienen.db → {db_filename}")
        else:
            import shutil
            shutil.copy('bienen.db', db_filename)
            print(f"✅ Migration: bienen.db → {db_filename}")
        
        os.rename('bienen.db', 'bienen_old.db')
        print("ℹ️  Umbenennung: bienen.db → bienen_old.db")
    else:
        print("📁 Keine bienen.db gefunden - wird beim Start erstellt")
    
    print("\n" + "=" * 60)
    print("✅ Setup abgeschlossen!")
    print("=" * 60)
    print("\n📋 Nächste Schritte:")
    print("   1. python app.py")
    print("   2. Browser: http://localhost:5000/login")
    print("   3. Setup-Script enthält die Login-Anleitung")
    print("\n⚠️  WICHTIG: Passwort nach dem ersten Login ändern!")
    print("=" * 60)


if __name__ == '__main__':
    try:
        setup_admin()
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
