#!/usr/bin/env python3
"""
setup_user.py
-----------------------------
Einfaches Setup-Script für User-Verwaltung
Erstellt den Admin-User "<USERNAME>"

Verwendung:
    python setup_user.py
"""

import os
import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime

def setup_admin():
    """Erstellt User-Datenbank und Admin-User"""
    
    print("=" * 60)
    print("BeeHiveTracker - User-Setup")
    print("=" * 60)
    
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
    
    # Prüfe ob User "<USERNAME>" bereits existiert
    cursor.execute('SELECT id FROM users WHERE username = ?', ('<USERNAME>',))
    existing = cursor.fetchone()
    
    if existing:
        print("⚠️  User '<USERNAME>' existiert bereits!")
        response = input("Passwort zurücksetzen? (j/n): ")
        if response.lower() == 'j':
            password_hash = generate_password_hash('<PASSWORD_REMOVED>', method='pbkdf2:sha256')
            cursor.execute('''
                UPDATE users 
                SET password_hash = ?, is_admin = 1, failed_login_attempts = 0, locked_until = NULL
                WHERE username = ?
            ''', (password_hash, '<USERNAME>'))
            conn.commit()
            print("✅ Passwort zurückgesetzt auf: <PASSWORD_REMOVED>")
        else:
            print("ℹ️  Keine Änderungen")
            conn.close()
            return
    else:
        # Admin-User erstellen
        print("\n👤 Erstelle Admin-User '<USERNAME>'...")
        password_hash = generate_password_hash('<PASSWORD_REMOVED>', method='pbkdf2:sha256')
        cursor.execute('''
            INSERT INTO users (username, password_hash, is_admin, created_at)
            VALUES (?, ?, 1, ?)
        ''', ('<USERNAME>', password_hash, datetime.utcnow()))
        conn.commit()
        print("✅ Admin-User '<USERNAME>' erstellt")
        print("   Benutzername: jos")
        print("   Passwort: <PASSWORD_REMOVED>")
    
    conn.close()
    
    # 2. Datenbank-Migration
    print("\n📊 Datenbank-Migration...")
    
    if os.path.exists('bienen.db'):
        if os.path.exists('bienen_jos.db'):
            print("⚠️  bienen_jos.db existiert bereits")
            response = input("Überschreiben mit bienen.db? (j/n): ")
            if response.lower() == 'j':
                import shutil
                backup = f"bienen_jos_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                shutil.copy('bienen_jos.db', backup)
                print(f"✅ Backup: {backup}")
                shutil.copy('bienen.db', 'bienen_jos.db')
                print("✅ Migration: bienen.db → bienen_jos.db")
        else:
            import shutil
            shutil.copy('bienen.db', 'bienen_jos.db')
            print("✅ Migration: bienen.db → bienen_jos.db")
        
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
    print("   3. Login: jos / <PASSWORD_REMOVED>")
    print("\n⚠️  WICHTIG: Passwort nach dem ersten Login ändern!")
    print("=" * 60)


if __name__ == '__main__':
    try:
        setup_admin()
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
