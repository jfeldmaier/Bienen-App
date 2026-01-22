"""
user_models.py
-----------------------------
Datenbankmodelle für User-Verwaltung und Authentifizierung

Wichtige Variablen und Klassen:
--------------------------------
user_db: SQLAlchemy-Objekt für die User-Datenbank (users.db)
User: Modell für einen Benutzer
    - id: Primärschlüssel
    - username: Benutzername (unique)
    - password_hash: Gehashtes Passwort (pbkdf2:sha256)
    - is_admin: Admin-Berechtigung
    - failed_login_attempts: Anzahl Fehlversuche
    - locked_until: Zeitpunkt bis Account gesperrt ist
    - created_at: Erstellungsdatum
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db  # Nutze dieselbe DB-Instanz


class User(UserMixin, db.Model):
    """User-Modell für Authentifizierung und Autorisierung"""
    
    __tablename__ = 'users'
    __bind_key__ = 'users'  # Nutze separate users.db via bind
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def set_password(self, password):
        """Setzt das Passwort (gehashed mit pbkdf2:sha256)"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Überprüft das Passwort"""
        return check_password_hash(self.password_hash, password)
    
    def is_locked(self):
        """Prüft, ob der Account gesperrt ist"""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
    
    def increment_failed_attempts(self):
        """Erhöht die Anzahl der Fehlversuche"""
        from datetime import timedelta
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 3:
            # Account für 30 Minuten sperren
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
    
    def reset_failed_attempts(self):
        """Setzt die Fehlversuche zurück (nach erfolgreichem Login)"""
        self.failed_login_attempts = 0
        self.locked_until = None
    
    def __repr__(self):
        return f'<User {self.username} (Admin: {self.is_admin})>'
