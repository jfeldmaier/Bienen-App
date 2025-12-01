"""
models.py
-----------------------------
Datenbankmodelle für die Bienen-App

Wichtige Variablen und Klassen:
--------------------------------
db: SQLAlchemy-Objekt für die Datenbank
BeeColony: Modell für ein Bienenvolk
    - id: Primärschlüssel
    - name: Name des Volks
    - location: Standort
    - queen_birth: Geburtsdatum der Königin
    - status: Status des Volks
    - notes: Notizen
    - inspections: Liste der zugehörigen Inspektionen
Inspection: Modell für eine Inspektion
    - id: Primärschlüssel
    - colony_id: Fremdschlüssel zum Bienenvolk
    - date: Datum der Inspektion
    - health: Gesundheitsstatus
    - honey_yield: Honigertrag
    - queen_seen: Königin gesichtet?
    - varroa_check: Varroa-Kontrolle
    - notes: Notizen
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime

# Datenbank-Objekt
db = SQLAlchemy()

# Modell für ein Bienenvolk
class BeeColony(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50), nullable=False)
        location = db.Column(db.String(100))
        queen_birth = db.Column(db.Date)
        queen_color = db.Column(db.String(10))  # Farbe der Königinnenmarkierung
        queen_number = db.Column(db.String(10))  # Nummer der Königin
        status = db.Column(db.String(20))
        notes = db.Column(db.Text)
        inspections = db.relationship('Inspection', backref='colony', cascade='all, delete-orphan')

# Modell für eine Inspektion
class Inspection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    colony_id = db.Column(db.Integer, db.ForeignKey('bee_colony.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)
    honey_yield = db.Column(db.Float)
    queen_seen = db.Column(db.Boolean)
    varroa_check = db.Column(db.String(120))
    notes = db.Column(db.Text)
    # Neue Felder für Inspektion
    mittelwaende = db.Column(db.Integer)  # Mittelwände (Anzahl)
    brutwaben = db.Column(db.Integer)     # Brutwaben (Anzahl)
    futterwaben = db.Column(db.Integer)   # Futterwaben (Anzahl)
    volksstaerke = db.Column(db.Integer)  # Volksstärke (1-5)
    sanftmut = db.Column(db.Integer)      # Sanftmut (1-5)
    vitalitaet = db.Column(db.Integer)    # Vitalität (1-5)
    brut = db.Column(db.Integer)          # Brut (1-5)
    drohnenbrut_geschnitten = db.Column(db.Boolean)  # Drohnenbrut geschnitten (ja/nein)
    images = db.relationship('InspectionImage', backref='inspection', cascade='all, delete-orphan')


# Modell für Inspektionsbilder
class InspectionImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inspection_id = db.Column(db.Integer, db.ForeignKey('inspection.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)  # z.B. "20251115_123045_abc123.jpg"
    uploaded_at = db.Column(db.DateTime, default=datetime.now)
    
    def get_relative_path(self):
        """Gibt den relativen Pfad zum Bild zurück (für Static-Serving)"""
        if self.inspection and self.inspection.date:
            date_str = self.inspection.date.strftime('%Y%m%d')
            return f'uploads/inspections/{date_str}/{self.filename}'
        return None
