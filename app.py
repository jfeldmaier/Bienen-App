# -----------------------------
# Bienen-App: Hauptanwendung
# -----------------------------
# Variablen- und Objektübersicht:
#
# app: Flask-Anwendung
# db: SQLAlchemy-Objekt für Datenbankzugriff
# BeeColony: Datenbankmodell für ein Bienenvolk
# Inspection: Datenbankmodell für eine Inspektion
# BeeColonyForm: WTForms-Formular für Bienenvölker
# InspectionForm: WTForms-Formular für Inspektionen
# BatchInspectionForm: WTForms-Formular für Mehrfach-Inspektionen
# voelker: Liste aller Bienenvölker (für Auswahl im Formular und Übersichten)
# voelker: Liste aller Bienenvölker (für Übersichten)
# inspektionen: Liste aller Inspektionen
# volk: Einzelnes Bienenvolk (Detailansicht)
# inspektion: Einzelne Inspektion (Bearbeitung)
#
# Wichtige Routen:
# /                      Startseite mit Übersicht
# /neues-volk            Neues Volk anlegen
# /batch-inspektion      Mehrere Inspektionen anlegen
# /neue-inspektion   Neue Inspektion anlegen
# /voelker           Völkerliste
# /inspektionen      Inspektionsliste
# /volk/<id>         Detailansicht eines Volkes
#

from datetime import datetime, date
from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory
from models import db, BeeColony, Inspection, InspectionImage
from forms import BeeColonyForm, InspectionForm, BatchInspectionForm
from upload_utils import save_inspection_images, delete_inspection_images
import os

# Wörterbuch für Königinnenfarben
QUEEN_COLORS = {
    'white': 'Weiß',
    'yellow': 'Gelb',
    'red': 'Rot',
    'green': 'Grün',
    'blue': 'Blau'
}

# Flask-App und Datenbank initialisieren
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bienen.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'biene'


BASE_UPLOAD_FOLDER = os.path.join(os.getcwd(), 'var', 'uploads')
app.config['UPLOAD_FOLDER'] = BASE_UPLOAD_FOLDER

db.init_app(app)

# Globale Variablen für Templates
@app.context_processor
def utility_processor():
    return {'queen_colors': QUEEN_COLORS}

# Datenbank automatisch erstellen, falls nicht vorhanden
with app.app_context():
    db.create_all()


# Startseite: Übersicht aller Bienenvölker
@app.route("/")
def home():
    voelker = BeeColony.query.all()
    return render_template('index.html', voelker=voelker)


@app.route('/neues-volk', methods=['GET', 'POST'])
def neues_volk():
    form = BeeColonyForm()
    if form.validate_on_submit():
        volk = BeeColony(
            name=form.name.data,
            location=form.location.data,
            queen_birth=form.queen_birth.data,
            status=form.status.data,
            notes=form.notes.data
        )
        db.session.add(volk)
        db.session.commit()
        flash('✅ Neues Bienenvolk wurde erfolgreich gespeichert!', 'success')
        return redirect(url_for('home'))
    return render_template('volk_form.html', form=form)



# Neue Inspektion anlegen
@app.route('/neue-inspektion', methods=['GET', 'POST'])
def neue_inspektion():
    voelker = BeeColony.query.all()
    form = InspectionForm()
    # Auswahlmöglichkeiten für das SelectField setzen
    form.colony_id.choices = [(v.id, v.name) for v in voelker]
    # colony_id ggf. aus Query-Parameter vorbelegen
    volk_id = request.args.get('colony_id', type=int)
    from datetime import date
    if request.method == 'GET':
        if volk_id:
            form.colony_id.data = volk_id
        if not form.date.data:
            form.date.data = date.today()
    if form.validate_on_submit():
        inspektion = Inspection(
            colony_id=form.colony_id.data,
            date=form.date.data,
            volksstaerke=request.form.get('volksstaerke', type=int),
            honey_yield=form.honey_yield.data,
            queen_seen=form.queen_seen.data,
            notes=form.notes.data,
            varroa_check=form.varroa_check.data,
            mittelwaende=request.form.get('mittelwaende', type=int),
            brutwaben=request.form.get('brutwaben', type=int),
            futterwaben=request.form.get('futterwaben', type=int),
            sanftmut=request.form.get('sanftmut', type=int),
            vitalitaet=request.form.get('vitalitaet', type=int),
            brut=request.form.get('brut', type=int),
            drohnenbrut_geschnitten=form.drohnenbrut_geschnitten.data
        )
        db.session.add(inspektion)
        db.session.commit()
        
        # Bilder speichern
        try:
            image_files = request.files.getlist('images')
            if image_files and image_files[0].filename != '':
                saved_filenames = save_inspection_images(image_files, form.date.data)
                for filename in saved_filenames:
                    img_record = InspectionImage(inspection_id=inspektion.id, filename=filename)
                    db.session.add(img_record)
                db.session.commit()
                if saved_filenames:
                    flash(f'✅ Inspektion mit {len(saved_filenames)} Bild(ern) gespeichert!', 'success')
                else:
                    flash('✅ Inspektion gespeichert (ohne Bilder).', 'success')
        except ValueError as e:
            flash(f'⚠️ Inspektion gespeichert, aber Fehler bei Bildern: {str(e)}', 'warning')
        except IOError as e:
            flash(f'⚠️ Inspektion gespeichert, aber Fehler beim Speichern: {str(e)}', 'warning')
        
        return redirect(url_for('volk_detail', volk_id=form.colony_id.data))
    return render_template('inspektion_form.html', form=form, voelker=voelker)


# Übersicht aller Bienenvölker
@app.route('/voelker')
def voelker_liste():
    voelker = BeeColony.query.all()
    return render_template('voelker_liste.html', voelker=voelker)


# Übersicht aller Inspektionen
@app.route('/inspektionen')
def inspektionen_liste():
    # Sortiere Inspektionen chronologisch (neueste zuerst)
    inspektionen = Inspection.query.order_by(Inspection.date.desc()).all()

    # Gruppiere nach Kalendertag (Datum selbst ist ein datetime.date)
    from itertools import groupby
    # groupby benötigt, dass gleiche Keys zusammenstehen. Da wir bereits nach
    # Inspection.date.desc() sortiert haben, werden gleiche Tage nacheinander
    # auftauchen und groupby funktioniert wie erwartet.
    inspektionen_by_day = [(day, list(items)) for day, items in groupby(inspektionen, key=lambda i: i.date)]

    return render_template('inspektionen_liste.html', inspektionen_by_day=inspektionen_by_day)


# Inspektion bearbeiten
@app.route('/inspektion/<int:id>/bearbeiten', methods=['GET', 'POST'])
def inspektion_bearbeiten(id):
    inspektion = Inspection.query.get_or_404(id)
    form = InspectionForm(obj=inspektion)
    voelker = BeeColony.query.all()
    form.colony_id.choices = [(v.id, v.name) for v in voelker]
    
    if request.method == 'GET':
        # Vorbelegung der Werte beim Laden des Formulars
        form.colony_id.data = inspektion.colony_id
        
    if form.validate_on_submit():
        # Werte einzeln setzen statt form.populate_obj zu verwenden
        inspektion.colony_id = form.colony_id.data
        inspektion.date = form.date.data
        inspektion.volksstaerke = request.form.get('volksstaerke', type=int)
        inspektion.honey_yield = form.honey_yield.data
        inspektion.queen_seen = form.queen_seen.data
        inspektion.notes = form.notes.data
        inspektion.varroa_check = form.varroa_check.data
        inspektion.mittelwaende = request.form.get('mittelwaende', type=int)
        inspektion.brutwaben = request.form.get('brutwaben', type=int)
        inspektion.futterwaben = request.form.get('futterwaben', type=int)
        inspektion.sanftmut = request.form.get('sanftmut', type=int)
        inspektion.vitalitaet = request.form.get('vitalitaet', type=int)
        inspektion.brut = request.form.get('brut', type=int)
        inspektion.drohnenbrut_geschnitten = form.drohnenbrut_geschnitten.data
        db.session.commit()
        
        # Neue Bilder speichern (zu bestehenden hinzufügen)
        try:
            image_files = request.files.getlist('images')
            if image_files and image_files[0].filename != '':
                saved_filenames = save_inspection_images(image_files, form.date.data)
                for filename in saved_filenames:
                    img_record = InspectionImage(inspection_id=inspektion.id, filename=filename)
                    db.session.add(img_record)
                db.session.commit()
                if saved_filenames:
                    flash(f'✅ Inspektion aktualisiert + {len(saved_filenames)} neue Bild(er)!', 'success')
                else:
                    flash('✅ Inspektion aktualisiert.', 'success')
            else:
                flash('✅ Inspektion wurde aktualisiert!', 'success')
        except (ValueError, IOError) as e:
            flash(f'⚠️ Inspektion aktualisiert, aber Fehler bei Bildern: {str(e)}', 'warning')
        
        return redirect(url_for('volk_detail', volk_id=inspektion.colony_id))
    return render_template('inspektion_form.html', form=form, bearbeiten=True, voelker=voelker, inspektion=inspektion)


# Inspektions-Detailansicht
@app.route('/inspektion/<int:id>')
def inspektion_detail(id):
    inspektion = Inspection.query.get_or_404(id)
    return render_template('inspektion_detail.html', inspektion=inspektion)

@app.route('/uploads/inspections/<date>/<filename>')
def uploaded_inspection_image(date, filename):
    # Korrekter Pfad: (Absoluter Pfad zu var/uploads) + /inspections/ + (datum)
    import os # os ist bereits importiert, aber zur Verdeutlichung
    # Der absolute Pfad zum Verzeichnis: /Pfad/zum/Projekt/var/uploads/inspections/YYYYMMDD
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'inspections', date)
    # send_from_directory sucht im angegebenen Verzeichnis (upload_path) nach der Datei (filename).
    return send_from_directory(upload_path, filename)

# @app.route('/uploads/inspections/<date>/<filename>')
# def uploaded_inspection_image(date, filename):
#     # Pfad: var/uploads/inspections/YYYYMMDD/filename
#     upload_dir = f"var/uploads/inspections/{date}"
#     return send_from_directory(upload_dir, filename)

# Detailansicht eines Volkes
@app.route('/volk/<int:volk_id>')
def volk_detail(volk_id):
    volk = BeeColony.query.get_or_404(volk_id)
    inspektionen = Inspection.query.filter_by(colony_id=volk.id).order_by(Inspection.date.desc()).all()
    return render_template('volk_detail.html', volk=volk, inspektionen=inspektionen)

# Status eines Volkes direkt ändern
@app.route('/volk/<int:volk_id>/status', methods=['POST'])
def volk_status_aendern(volk_id):
    volk = BeeColony.query.get_or_404(volk_id)
    neuer_status = request.form.get('status')
    if neuer_status in ['stark', 'mittel', 'schwach']:
        volk.status = neuer_status
        db.session.commit()
    return redirect(url_for('volk_detail', volk_id=volk.id))

# Batch-Inspektion für mehrere Völker
@app.route('/batch-inspektion', methods=['GET', 'POST'])
def batch_inspektion():
    form = BatchInspectionForm()
    voelker = BeeColony.query.all()
    form.colony_ids.choices = [(v.id, v.name) for v in voelker]
    
    if request.method == 'POST' and form.validate_on_submit():
        colony_ids = request.form.getlist('colony_ids', type=int)
        if colony_ids:
            erfolgreiche = 0
            for colony_id in colony_ids:
                inspektion = Inspection(
                    colony_id=colony_id,
                    date=form.date.data,
                    volksstaerke=request.form.get('volksstaerke', type=int),
                    sanftmut=request.form.get('sanftmut', type=int),
                    vitalitaet=request.form.get('vitalitaet', type=int),
                    brut=request.form.get('brut', type=int),
                    honey_yield=form.honey_yield.data,
                    queen_seen=form.queen_seen.data,
                    notes=form.notes.data,
                    varroa_check=form.varroa_check.data,
                    mittelwaende=form.mittelwaende.data,
                    brutwaben=form.brutwaben.data,
                    futterwaben=form.futterwaben.data,
                    drohnenbrut_geschnitten=form.drohnenbrut_geschnitten.data
                )
                db.session.add(inspektion)
                erfolgreiche += 1
            
            db.session.commit()
            flash(f'✅ {erfolgreiche} Inspektionen wurden erfolgreich angelegt!', 'success')
            return redirect(url_for('inspektionen_liste'))
        else:
            flash('❌ Bitte wählen Sie mindestens ein Volk aus.', 'error')
    
    # Standardwerte setzen
    if request.method == 'GET':
        form.date.data = datetime.now()
    
    return render_template('batch_inspektion_form.html', form=form, voelker=voelker)

# Bienenvolk bearbeiten
@app.route('/volk/<int:volk_id>/bearbeiten', methods=['GET', 'POST'])
def volk_bearbeiten(volk_id):
    volk = BeeColony.query.get_or_404(volk_id)
    form = BeeColonyForm(obj=volk)
    if form.validate_on_submit():
        form.populate_obj(volk)
        db.session.commit()
        return redirect(url_for('volk_detail', volk_id=volk.id))
    return render_template('volk_form.html', form=form, bearbeiten=True)


# Bienenvolk löschen
@app.route('/volk/<int:volk_id>/loeschen', methods=['POST'])
def volk_loeschen(volk_id):
    volk = BeeColony.query.get_or_404(volk_id)
    db.session.delete(volk)
    db.session.commit()
    return redirect(url_for('voelker_liste'))

# Inspektion löschen
@app.route('/inspektion/<int:id>/loeschen', methods=['POST'])
def inspektion_loeschen(id):
    inspektion = Inspection.query.get_or_404(id)
    volk_id = inspektion.colony_id
    
    # Bilder und Dateien löschen
    try:
        delete_inspection_images(id)
    except Exception as e:
        flash(f'⚠️ Fehler beim Löschen der Bilder: {str(e)}', 'warning')
    
    db.session.delete(inspektion)
    db.session.commit()
    flash('✅ Inspektion wurde gelöscht!', 'success')
    return redirect(url_for('volk_detail', volk_id=volk_id))


# Batch-Löschen von Inspektionen (markierte Einträge)
@app.route('/inspektionen/loeschen', methods=['POST'])
def inspektionen_loeschen():
    ids = request.form.getlist('inspection_ids')
    if not ids:
        flash('❌ Keine Inspektionen ausgewählt.', 'error')
        return redirect(url_for('inspektionen_liste'))

    # Konvertiere zu int und lösche
    deleted = 0
    for _id in ids:
        try:
            insp_id = int(_id)
        except (TypeError, ValueError):
            continue
        ins = Inspection.query.get(insp_id)
        if ins:
            # Bilder löschen
            try:
                delete_inspection_images(insp_id)
            except Exception as e:
                print(f"Warnung: Fehler beim Löschen von Bildern für Inspektion {insp_id}: {e}")
            db.session.delete(ins)
            deleted += 1

    db.session.commit()
    flash(f'✅ {deleted} Inspektion(en) gelöscht.', 'success')
    return redirect(url_for('inspektionen_liste'))

# App-Start
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')