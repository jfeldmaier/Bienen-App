#!/usr/bin/env python3
"""
init_admin.py
-----------------------------
Initialisierungs-Script für die User-Verwaltung
Erstellt einen Admin-User und migriert die Datenbank

Verwendung:
    python init_admin.py
"""

import os
import sys

def load_default_credentials():
    """Liest Standard-Anmeldedaten aus default_user.txt"""
    if not os.path.exists('default_user.txt'):
        print("❌ Fehler: default_user.txt nicht gefunden!")
        print("Bitte erstellen Sie die Datei basierend auf default_user.example.txt")
        sys.exit(1)
    
    credentials = {}
    with open('default_user.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                credentials[key.strip()] = value.strip()
    
    if 'USERNAME' not in credentials or 'PASSWORD' not in credentials:
        print("❌ Fehler: USERNAME oder PASSWORD nicht in default_user.txt gefunden!")
        sys.exit(1)
    
    return credentials['USERNAME'], credentials['PASSWORD']

def init_admin_user():
    """Erstellt Admin-User und initialisiert Datenbanken"""
    
    # Lade Anmeldedaten aus Konfigurationsdatei
    admin_username, admin_password = load_default_credentials()
    
    print("=" * 60)
    print("BeeHiveTracker - User-Verwaltung Initialisierung")
    print("=" * 60)
    
    
    # Importiere die bereits konfigurierte App aus app.py
    # Dies muss hier gemacht werden, damit die DB-Instanzen korrekt sind
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from user_models import User
    from datetime import datetime
    import shutil
    
    # Bestimme DB-URI basierend auf Admin-Username
    db_uri = f'sqlite:///bienen_{admin_username}.db'
    
    # Erstelle minimale App-Konfiguration
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_BINDS'] = {'users': 'sqlite:///users.db'}
    app.config['SECRET_KEY'] = 'init-temp-key'
    
    # Erstelle neue DB-Instanzen (nicht aus models/user_models importieren)
    from flask_sqlalchemy import SQLAlchemy
    user_db = SQLAlchemy(app)
    db = SQLAlchemy(app)
    
    # User-Modell definieren (Kopie von user_models.py)
    from flask_login import UserMixin
    from werkzeug.security import generate_password_hash, check_password_hash
    from datetime import datetime
    
    class UserInit(user_db.Model):
        __tablename__ = 'users'
        __bind_key__ = 'users'
        id = user_db.Column(user_db.Integer, primary_key=True)
        username = user_db.Column(user_db.String(50), unique=True, nullable=False)
        password_hash = user_db.Column(user_db.String(255), nullable=False)
        is_admin = user_db.Column(user_db.Boolean, default=False)
        failed_login_attempts = user_db.Column(user_db.Integer, default=0)
        locked_until = user_db.Column(user_db.DateTime, nullable=True)
        created_at = user_db.Column(user_db.DateTime, default=datetime.utcnow)
        
        def set_password(self, password):
            self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    with app.app_context():
        print("\n📁 Erstelle User-Datenbank (users.db)...")
        user_db.create_all()
        print("✅ User-Datenbank erstellt")
        
        # 2. Prüfe ob Admin-User bereits existiert
        existing_user = UserInit.query.filter_by(username=admin_username).first()
        if existing_user:
            print(f"\n⚠️  User '{admin_username}' existiert bereits!")
            response = input("Möchten Sie das Passwort zurücksetzen? (j/n): ")
            if response.lower() == 'j':
                existing_user.set_password(admin_password)
                existing_user.is_admin = True
                user_db.session.commit()
                print("✅ Admin-User aktualisiert")
            else:
                print("ℹ️  Keine Änderungen vorgenommen")
            return
        
        # 3. Admin-User erstellen
        print(f"\n👤 Erstelle Admin-User '{admin_username}'...")
        admin_user = UserInit(username=admin_username, is_admin=True)
        admin_user.set_password(admin_password)
        user_db.session.add(admin_user)
        user_db.session.commit()
        print("✅ Admin-User erstellt")
        
        # Bestimme DB-Dateiname
        db_filename = f'bienen_{admin_username}.db'
        
        print("\n📊 Datenbank-Migration...")
        if os.path.exists('bienen.db'):
            if os.path.exists(db_filename):
                print(f"⚠️  {db_filename} existiert bereits!")
                response = input("Möchten Sie die bestehende bienen.db überschreiben? (j/n): ")
                if response.lower() != 'j':
                    print("ℹ️  Migration übersprungen")
                else:
                    from datetime import datetime
                    import shutil
                    backup_name = f"bienen_{admin_username}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                    shutil.copy(db_filename, backup_name)
                    print(f"✅ Backup erstellt: {backup_name}")
                    shutil.copy('bienen.db', db_filename)
                    print(f"✅ Datenbank migriert: bienen.db → {db_filename} (überschrieben)")
            else:
                # Kopiere bienen.db nach bienen_{username}.db
                import shutil
                shutil.copy('bienen.db', db_filename)
                print(f"✅ Datenbank migriert: bienen.db → {db_filename}")
            
            os.rename('bienen.db', 'bienen_old.db')
            print("ℹ️  Alte Datenbank umbenannt: bienen.db → bienen_old.db")
        else:
            print("📁 Keine bestehende bienen.db gefunden")
            print("   Eine leere Datenbank wird beim ersten Start automatisch erstellt")
    
    print("\n" + "=" * 60)
    print("✅ Initialisierung abgeschlossen!")
    print("=" * 60)
    print("\n📋 Nächste Schritte:")
    print("   1. Starte die Anwendung: python app.py")
    print("   2. Öffne im Browser: http://localhost:5000/login")
    print("   3. Melde dich mit den Anmeldedaten aus default_user.txt an")
    print("\n⚠️  WICHTIG: Ändere das Passwort nach dem ersten Login!")
    print("=" * 60)


if __name__ == '__main__':
    try:
        init_admin_user()
    except Exception as e:
        print(f"\n❌ Fehler bei der Initialisierung: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
