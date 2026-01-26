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

from datetime import datetime, date, timedelta
from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory, session, g, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from functools import wraps
from models import db, BeeColony, Inspection, InspectionImage
from user_models import User
from forms import BeeColonyForm, InspectionForm, BatchInspectionForm, LoginForm, UserCreateForm
from upload_utils import save_inspection_images, delete_inspection_images
import os
import secrets
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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

# Environment-basierte Konfiguration
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
DEBUG_MODE = os.getenv('DEBUG', 'False').lower() == 'true'

# Sicherer SECRET_KEY für Produktion (generiert falls nicht vorhanden)
SECRET_KEY_FILE = 'secret_key.txt'
if os.path.exists(SECRET_KEY_FILE):
    with open(SECRET_KEY_FILE, 'r') as f:
        app.config['SECRET_KEY'] = f.read().strip()
else:
    # Generiere neuen sicheren Key
    new_key = secrets.token_hex(32)
    with open(SECRET_KEY_FILE, 'w') as f:
        f.write(new_key)
    app.config['SECRET_KEY'] = new_key

# Session-Konfiguration für Sicherheit und 10 Tage Gültigkeit
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=10)
# In Production mit HTTPS: SESSION_COOKIE_SECURE aktivieren
app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'

# Datenbank-Konfiguration (absolute Pfade im Instance-Ordner)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
BASE_INSTANCE_DIR = os.path.abspath(os.getenv('DATABASE_PATH', os.path.join(app.root_path, 'var', 'app-instance')))
os.makedirs(BASE_INSTANCE_DIR, exist_ok=True)
DEFAULT_DB_PATH = os.path.join(BASE_INSTANCE_DIR, 'bienen_jos.db')
USERS_DB_PATH = os.path.join(BASE_INSTANCE_DIR, 'users.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DEFAULT_DB_PATH}'  # Default, wird dynamisch gesetzt
app.config['SQLALCHEMY_BINDS'] = {'users': f'sqlite:///{USERS_DB_PATH}'}  # Separate User-DB

BASE_UPLOAD_FOLDER = os.path.abspath(os.getenv('UPLOAD_FOLDER', os.path.join(os.getcwd(), 'var', 'uploads')))
app.config['UPLOAD_FOLDER'] = BASE_UPLOAD_FOLDER

# Datenbank initialisieren
db.init_app(app)

# Production-Logging konfigurieren
if not DEBUG_MODE:
    # Log-Verzeichnis erstellen
    log_dir = os.path.dirname(os.getenv('LOG_FILE', '/var/log/beehivetracker/app.log'))
    if log_dir and not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
        except PermissionError:
            # Fallback zu lokalem Verzeichnis
            log_dir = os.path.join(app.root_path, 'logs')
            os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.getenv('LOG_FILE', os.path.join(log_dir, 'app.log'))
    log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
    
    # File-Handler mit Rotation (max 10MB, 10 Backups)
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=10)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)
    app.logger.info('BeeHiveTracker gestartet im Production-Modus')

# Security Headers mit Flask-Talisman (nur in Production)
if not DEBUG_MODE:
    Talisman(app,
        force_https=False,  # Cloudflare handhabt HTTPS
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,  # 1 Jahr
        content_security_policy={
            'default-src': "'self'",
            'script-src': ["'self'", "'unsafe-inline'", 'cdn.jsdelivr.net'],
            'style-src': ["'self'", "'unsafe-inline'", 'cdn.jsdelivr.net'],
            'img-src': ["'self'", 'data:'],
            'font-src': ["'self'", 'cdn.jsdelivr.net']
        },
        content_security_policy_nonce_in=['script-src'],
        frame_options='DENY',
        x_xss_protection=True
    )

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Bitte melden Sie sich an, um auf diese Seite zuzugreifen.'
login_manager.login_message_category = 'warning'

# Rate Limiter Setup (3 Fehlversuche pro 30 Minuten)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

@login_manager.user_loader
def load_user(user_id):
    """User-Loader für Flask-Login"""
    return db.session.get(User, int(user_id))

# Hilfsfunktion: DB-URI für User ermitteln
def get_user_db_uri(username):
    """Gibt den absoluten Datenbank-Pfad für einen User zurück (im Instance-Ordner).
    Für 'jos' wird eine vorhandene bienen.db bevorzugt verwendet.
    """
    if username == 'jos':
        jos_legacy = os.path.join(BASE_INSTANCE_DIR, 'bienen.db')
        if os.path.exists(jos_legacy):
            return f'sqlite:///{jos_legacy}'
    filename = f'bienen_{username}.db'
    return f'sqlite:///{os.path.join(BASE_INSTANCE_DIR, filename)}'


# Admin-Decorator
def admin_required(f):
    """Decorator: Route nur für Admins zugänglich"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('⛔ Sie benötigen Administrator-Rechte für diese Aktion.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function


# Dynamische Datenbank-Bindung vor jedem Request
@app.before_request
def before_request():
    """Lädt die richtige User-Datenbank vor jedem Request"""
    if current_user.is_authenticated:
        # Setze DB-URI basierend auf eingeloggtem User
        db_uri = get_user_db_uri(current_user.username)
        if app.config.get('SQLALCHEMY_DATABASE_URI') != db_uri:
            app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
            db.session.remove()  # Alte Session schließen
            db.engine.dispose()  # Engine neu initialisieren
        
        # Session als permanent markieren (verlängert bei Aktivität)
        session.permanent = True


# Globale Variablen für Templates
@app.context_processor
def utility_processor():
    return {'queen_colors': QUEEN_COLORS}


# Datenbanken automatisch erstellen, falls nicht vorhanden
with app.app_context():
    db.create_all()  # Erstellt alle Tabellen inkl. users (via bind)


# ========================================
# HEALTH CHECK & ERROR HANDLER
# ========================================

@app.route('/health')
def health_check():
    """Health-Check-Endpoint für Monitoring und Load-Balancer"""
    try:
        # Teste Datenbankverbindung
        db.session.execute(db.text('SELECT 1'))
        return {'status': 'healthy', 'database': 'connected'}, 200
    except Exception as e:
        app.logger.error(f'Health-Check fehlgeschlagen: {e}')
        return {'status': 'unhealthy', 'error': str(e)}, 503


@app.errorhandler(404)
def not_found_error(error):
    """Custom 404 Error Handler"""
    app.logger.warning(f'404 Error: {request.url}')
    return render_template('base.html', 
                         content='<div class="alert alert-warning"><h3>404 - Seite nicht gefunden</h3><p>Die angeforderte Seite existiert nicht.</p><a href="/" class="btn btn-primary">Zur Startseite</a></div>'), 404


@app.errorhandler(500)
def internal_error(error):
    """Custom 500 Error Handler"""
    app.logger.error(f'500 Error: {error}')
    db.session.rollback()  # Rollback bei DB-Fehler
    return render_template('base.html',
                         content='<div class="alert alert-danger"><h3>500 - Interner Serverfehler</h3><p>Ein unerwarteter Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.</p><a href="/" class="btn btn-primary">Zur Startseite</a></div>'), 500


# ========================================
# AUTHENTIFIZIERUNG: Login/Logout
# ========================================

@app.route("/login", methods=['GET', 'POST'])
@limiter.limit("10 per minute")  # Rate Limiting für Login-Versuche
def login():
    """Login-Seite"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # User aus User-DB laden
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None:
            flash('❌ Ungültiger Benutzername oder Passwort.', 'danger')
            return render_template('login.html', form=form)
        
        # Account-Sperre prüfen
        if user.is_locked():
            remaining_time = (user.locked_until - datetime.utcnow()).total_seconds() / 60
            flash(f'🔒 Ihr Account ist gesperrt. Versuchen Sie es in {int(remaining_time)} Minuten erneut.', 'danger')
            return render_template('login.html', form=form)
        
        # Passwort prüfen
        if not user.check_password(form.password.data):
            user.increment_failed_attempts()
            db.session.commit()
            
            if user.is_locked():
                flash('🔒 Zu viele Fehlversuche. Ihr Account wurde für 30 Minuten gesperrt.', 'danger')
            else:
                remaining = 3 - user.failed_login_attempts
                flash(f'❌ Ungültiger Benutzername oder Passwort. Noch {remaining} Versuch(e) übrig.', 'danger')
            
            return render_template('login.html', form=form)
        
        # Login erfolgreich
        user.reset_failed_attempts()
        db.session.commit()
        
        # remember_me = True für 10-Tage-Session
        login_user(user, remember=form.remember_me.data or True)
        session.permanent = True
        
        flash(f'✅ Willkommen zurück, {user.username}!', 'success')
        
        # Redirect zu ursprünglich angefragter Seite
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('home'))
    
    return render_template('login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    """Logout"""
    logout_user()
    flash('👋 Sie wurden erfolgreich abgemeldet.', 'info')
    return redirect(url_for('login'))


# ========================================
# ADMIN: User-Verwaltung
# ========================================

@app.route("/admin/users")
@admin_required
def admin_users():
    """User-Verwaltungsoberfläche (nur für Admins)"""
    users = User.query.order_by(User.created_at.desc()).all()
    form = UserCreateForm()
    return render_template('admin_users.html', users=users, form=form)


@app.route("/admin/users/create", methods=['POST'])
@admin_required
def admin_user_create():
    """Neuen User anlegen (nur für Admins)"""
    form = UserCreateForm()
    
    if form.validate_on_submit():
        # Prüfe ob Username bereits existiert
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('❌ Ein Benutzer mit diesem Namen existiert bereits.', 'danger')
            return redirect(url_for('admin_users'))
        
        # Neuen User erstellen
        new_user = User(
            username=form.username.data,
            is_admin=form.is_admin.data
        )
        new_user.set_password(form.password.data)
        
        db.session.add(new_user)
        db.session.commit()
        
        # Leere Datenbank für neuen User erstellen
        user_db_uri = get_user_db_uri(form.username.data)
        temp_config = app.config['SQLALCHEMY_DATABASE_URI']
        app.config['SQLALCHEMY_DATABASE_URI'] = user_db_uri
        
        with app.app_context():
            db.create_all()
        
        app.config['SQLALCHEMY_DATABASE_URI'] = temp_config
        
        flash(f'✅ Benutzer "{form.username.data}" wurde erfolgreich erstellt.', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'❌ {field}: {error}', 'danger')
    
    return redirect(url_for('admin_users'))


@app.route("/admin/users/<int:user_id>/delete", methods=['POST'])
@admin_required
def admin_user_delete(user_id):
    """User löschen (nur für Admins)"""
    user = db.session.get(User, user_id) or abort(404)
    
    # Verhindere Selbstlöschung
    if user.id == current_user.id:
        flash('❌ Sie können Ihren eigenen Account nicht löschen.', 'danger')
        return redirect(url_for('admin_users'))
    
    username = user.username
    
    # User aus DB löschen
    db.session.delete(user)
    db.session.commit()
    
    # Datenbank-Datei umbenennen mit _deleted Suffix
    db_file = os.path.abspath(os.path.join(BASE_INSTANCE_DIR, f'bienen_{username}.db'))
    if os.path.exists(db_file):
        deleted_file = os.path.abspath(os.path.join(BASE_INSTANCE_DIR, f'bienen_{username}_deleted_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'))
        os.rename(db_file, deleted_file)
        flash(f'✅ Benutzer "{username}" wurde gelöscht. Datenbank wurde archiviert als: {deleted_file}', 'success')
    else:
        flash(f'✅ Benutzer "{username}" wurde gelöscht.', 'success')
    
    return redirect(url_for('admin_users'))


# ========================================
# HAUPTANWENDUNG: Völker & Inspektionen
# ========================================

# Startseite: Übersicht aller Bienenvölker
@app.route("/")
@login_required
def home():
    voelker = BeeColony.query.all()
    return render_template('index.html', voelker=voelker)


@app.route('/neues-volk', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
def voelker_liste():
    voelker = BeeColony.query.all()
    return render_template('voelker_liste.html', voelker=voelker)


# Übersicht aller Inspektionen
@app.route('/inspektionen')
@login_required
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
@login_required
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
@login_required
def inspektion_detail(id):
    inspektion = Inspection.query.get_or_404(id)
    return render_template('inspektion_detail.html', inspektion=inspektion)

@app.route('/uploads/inspections/<date>/<filename>')
@login_required
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
@login_required
def volk_detail(volk_id):
    volk = BeeColony.query.get_or_404(volk_id)
    inspektionen = Inspection.query.filter_by(colony_id=volk.id).order_by(Inspection.date.desc()).all()
    return render_template('volk_detail.html', volk=volk, inspektionen=inspektionen)

# Status eines Volkes direkt ändern
@app.route('/volk/<int:volk_id>/status', methods=['POST'])
@login_required
def volk_status_aendern(volk_id):
    volk = BeeColony.query.get_or_404(volk_id)
    neuer_status = request.form.get('status')
    if neuer_status in ['stark', 'mittel', 'schwach']:
        volk.status = neuer_status
        db.session.commit()
    return redirect(url_for('volk_detail', volk_id=volk.id))

# Batch-Inspektion für mehrere Völker
@app.route('/batch-inspektion', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
def volk_loeschen(volk_id):
    volk = BeeColony.query.get_or_404(volk_id)
    db.session.delete(volk)
    db.session.commit()
    return redirect(url_for('voelker_liste'))

# Inspektion löschen
@app.route('/inspektion/<int:id>/loeschen', methods=['POST'])
@login_required
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
@login_required
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
    # Nur für lokales Development - in Production wird Gunicorn verwendet
    host = os.getenv('SERVER_HOST', '0.0.0.0')
    port = int(os.getenv('SERVER_PORT', 5000))
    app.run(debug=DEBUG_MODE, host=host, port=port)