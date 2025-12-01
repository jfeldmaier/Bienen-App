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
    IntegerField
)
from wtforms.validators import DataRequired, Optional

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
