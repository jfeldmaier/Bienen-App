"""
forms.py
-----------------------------
Formulare für die Bienen-App (WTForms)

Wichtige Variablen und Klassen:
--------------------------------
BeeColonyForm: Formular für ein Bienenvolk
    - name: Name des Volks
    - location: Standort
    - queen_birth: Geburtsdatum der Königin
    - status: Status des Volks
    - notes: Notizen
InspectionForm: Formular für eine Inspektion
    - colony_id: Zugehöriges Volk (SelectField)
    - date: Datum der Inspektion
    - volksstaerke: Volksstärke (1-5 Sterne)
    - honey_yield: Honigertrag
    - queen_seen: Königin gesichtet?
    - notes: Beobachtungen
    - varroa_check: Varroa-Kontrolle
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms.fields import (
    StringField, 
    DateField, 
    TextAreaField, 
    FloatField, 
    BooleanField, 
    SelectField,
    SelectMultipleField, 
    SubmitField, 
    IntegerField,
    PasswordField
)
from wtforms.validators import DataRequired, Optional, EqualTo, ValidationError, Length
import re

# Formular für ein Bienenvolk
class BeeColonyForm(FlaskForm):
        name = StringField('Name des Volks', validators=[DataRequired()])
        location = StringField('Standort', validators=[Optional()])
        queen_birth = DateField('Geburtsdatum der Königin', format='%Y-%m-%d', validators=[Optional()])
        queen_color = SelectField('Farbe der Königinnenmarkierung', 
                                choices=[('white', 'Weiß'), 
                                        ('yellow', 'Gelb'), 
                                        ('red', 'Rot'), 
                                        ('green', 'Grün'), 
                                        ('blue', 'Blau')], 
                                validators=[Optional()])
        queen_number = StringField('Nummer der Königin', validators=[Optional()])
        status = SelectField('Status', choices=[('stark', 'Stark'), ('mittel', 'Mittel'), ('schwach', 'Schwach')], validators=[Optional()])
        notes = TextAreaField('Notizen', validators=[Optional()])
        submit = SubmitField('Speichern')

# Formular für eine Inspektion
class InspectionForm(FlaskForm):
        colony_id = SelectField('Volk', coerce=int, validators=[DataRequired()])
        date = DateField('Datum', format='%Y-%m-%d', validators=[Optional()])
        volksstaerke = IntegerField('Volksstärke', validators=[Optional()])
        sanftmut = IntegerField('Sanftmut', validators=[Optional()])
        vitalitaet = IntegerField('Vitalität', validators=[Optional()])
        brut = IntegerField('Brut', validators=[Optional()])
        honey_yield = FloatField('Honigertrag (kg)', validators=[Optional()])
        queen_seen = BooleanField('Königin gesichtet?', validators=[Optional()])
        notes = TextAreaField('Beobachtungen', validators=[Optional()])
        varroa_check = TextAreaField('Varroa-Kontrolle', validators=[Optional()])
        mittelwaende = IntegerField('Mittelwände', validators=[Optional()])
        brutwaben = IntegerField('Brutwaben', validators=[Optional()])
        futterwaben = IntegerField('Futterwaben', validators=[Optional()])
        drohnenbrut_geschnitten = BooleanField('Drohnenbrut geschnitten?', validators=[Optional()])
        images = FileField('Inspektionsbilder', render_kw={'multiple': True})

class BatchInspectionForm(FlaskForm):
        colony_ids = SelectMultipleField('Völker', coerce=int, validators=[DataRequired()])
        date = DateField('Datum', format='%Y-%m-%d', validators=[DataRequired()])
        volksstaerke = IntegerField('Volksstärke', validators=[Optional()])
        sanftmut = IntegerField('Sanftmut', validators=[Optional()])
        vitalitaet = IntegerField('Vitalität', validators=[Optional()])
        brut = IntegerField('Brut', validators=[Optional()])
        honey_yield = FloatField('Honigertrag (kg)', validators=[Optional()])
        queen_seen = BooleanField('Königin gesichtet?', validators=[Optional()])
        mittelwaende = IntegerField('Mittelwände', validators=[Optional()])
        brutwaben = IntegerField('Brutwaben', validators=[Optional()])
        futterwaben = IntegerField('Futterwaben', validators=[Optional()])
        drohnenbrut_geschnitten = BooleanField('Drohnenbrut geschnitten?', validators=[Optional()])
        notes = TextAreaField('Beobachtungen', validators=[Optional()])
        varroa_check = StringField('Varroa-Kontrolle', validators=[Optional()])
        submit = SubmitField('Speichern')


# Formular für Login
class LoginForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    remember_me = BooleanField('Angemeldet bleiben')
    submit = SubmitField('Anmelden')


# Formular für User-Erstellung
class UserCreateForm(FlaskForm):
    username = StringField('Benutzername', validators=[
        DataRequired(), 
        Length(min=3, max=50, message='Benutzername muss zwischen 3 und 50 Zeichen lang sein')
    ])
    password = PasswordField('Passwort', validators=[
        DataRequired(),
        Length(min=10, message='Passwort muss mindestens 10 Zeichen lang sein')
    ])
    password_confirm = PasswordField('Passwort wiederholen', validators=[
        DataRequired(),
        EqualTo('password', message='Passwörter müssen übereinstimmen')
    ])
    is_admin = BooleanField('Administrator-Rechte')
    submit = SubmitField('Benutzer erstellen')
    
    def validate_password(self, field):
        """
        Passwort-Validierung nach den Anforderungen:
        - Mindestens ein Großbuchstabe
        - Mindestens ein Kleinbuchstabe  
        - Mindestens eine Zahl
        - Mindestens ein Sonderzeichen
        """
        password = field.data
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Passwort muss mindestens einen Großbuchstaben enthalten')
        
        if not re.search(r'[a-z]', password):
            raise ValidationError('Passwort muss mindestens einen Kleinbuchstaben enthalten')
        
        if not re.search(r'[0-9]', password):
            raise ValidationError('Passwort muss mindestens eine Zahl enthalten')
        
        if not re.search(r'[^A-Za-z0-9]', password):
            raise ValidationError('Passwort muss mindestens ein Sonderzeichen enthalten')
