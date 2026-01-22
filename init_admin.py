#!/usr/bin/env python3
"""
init_admin.py
-----------------------------
Initialisierungs-Script für die User-Verwaltung
Erstellt den Admin-User "<USERNAME>" und migriert die Datenbank

Verwendung:
    python init_admin.py
"""

import os
import sys
# Wichtig: app.py importieren um die korrekt konfigurierten DB-Instanzen zu verwenden
import sys
import os

def init_admin_user():
    """Erstellt Admin-User und initialisiert Datenbanken"""
    
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
    
    # Erstelle minimale App-Konfiguration
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bienen_jos.db'
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
        existing_user = UserInit.query.filter_by(username='<USERNAME>').first()
        if existing_user:
            print("\n⚠️  User '<USERNAME>' existiert bereits!")
            response = input("Möchten Sie das Passwort zurücksetzen? (j/n): ")
            if response.lower() == 'j':
                existing_user.set_password('<PASSWORD_REMOVED>')
                existing_user.is_admin = True
                user_db.session.commit()
                print("✅ Passwort für '<USERNAME>' wurde zurückgesetzt auf: <PASSWORD_REMOVED>")
            else:
                print("ℹ️  Keine Änderungen vorgenommen")
            return
        
        # 3. Admin-User erstellen
        print("\n👤 Erstelle Admin-User '<USERNAME>'...")
        admin_user = UserInit(username='<USERNAME>', is_admin=True)
        admin_user.set_password('<PASSWORD_REMOVED>')
        user_db.session.add(admin_user)
        user_db.session.commit()
        print("✅ Admin-User '<USERNAME>' erstellt")
        print("   Benutzername: jos")
        print("   Passwort: <PASSWORD_REMOVED>")
        print("   Admin-Rechte: Ja")
        
        print("\n📊 Datenbank-Migration...")
        if os.path.exists('bienen.db'):
            if os.path.exists('bienen_jos.db'):
                print("⚠️  bienen_jos.db existiert bereits!")
                response = input("Möchten Sie die bestehende bienen.db überschreiben? (j/n): ")
                if response.lower() != 'j':
                    print("ℹ️  Migration übersprungen")
                else:
                    from datetime import datetime
                    import shutil
                    backup_name = f"bienen_jos_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                    shutil.copy('bienen_jos.db', backup_name)
                    print(f"✅ Backup erstellt: {backup_name}")
                    shutil.copy('bienen.db', 'bienen_jos.db')
                    print("✅ Datenbank migriert: bienen.db → bienen_jos.db (überschrieben)")
            else:
                # Kopiere bienen.db nach bienen_jos.db
                import shutil
                shutil.copy('bienen.db', 'bienen_jos.db')
                print("✅ Datenbank migriert: bienen.db → bienen_jos.db")
            
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
    print("   3. Melde dich an mit:")
    print("      Benutzername: jos")
    print("      Passwort: <PASSWORD_REMOVED>")
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
