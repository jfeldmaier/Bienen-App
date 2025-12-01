"""
upload_utils.py
-----------------------------
Hilfsfunktionen für Datei-Uploads zu Inspektionen
- Validierung von Dateitypen und -größen
- Speicherung in datierten Ordnern
- Cleanup beim Löschen von Inspektionen
"""

import os
import shutil
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

# Konfiguration
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
MAX_FILE_SIZE = 7 * 1024 * 1024  # 5 MB pro Bild
UPLOADS_DIR = 'var/uploads/inspections'


def allowed_file(filename: str) -> bool:
    """Prüft, ob die Dateiendung erlaubt ist."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_inspection_image_dir(inspection_date) -> str:
    """Gibt den Pfad zum Upload-Ordner für ein Inspektionsdatum zurück.
    
    Format: var/uploads/inspections/YYYYMMDD/
    """
    if inspection_date is None:
        raise ValueError("Inspektionsdatum ist erforderlich")
    
    date_str = inspection_date.strftime('%Y%m%d')
    upload_path = os.path.join(UPLOADS_DIR, date_str)
    return upload_path


def create_upload_directory(upload_path: str) -> None:
    """Erstellt das Upload-Verzeichnis, falls es nicht existiert."""
    os.makedirs(upload_path, exist_ok=True)


def save_inspection_images(files_list, inspection_date) -> list:
    """Speichert mehrere Inspektionsbilder und gibt eine Liste mit Dateinamen zurück.
    
    Args:
        files_list: Liste von FileStorage-Objekten aus request.files.getlist()
        inspection_date: datetime.date Objekt der Inspektion
    
    Returns:
        Liste mit gespeicherten Dateinamen oder leere Liste bei Fehler
    
    Raises:
        ValueError: Wenn Inspektionsdatum fehlt oder Validierung fehlschlägt
    """
    saved_filenames = []
    
    if not files_list or len(files_list) == 0:
        return saved_filenames
    
    upload_path = get_inspection_image_dir(inspection_date)
    create_upload_directory(upload_path)
    
    for file in files_list:
        # Leere Einträge überspringen
        if not file or file.filename == '':
            continue
        
        # Validierung
        if not allowed_file(file.filename):
            raise ValueError(
                f"Dateityp nicht erlaubt: {file.filename}. "
                f"Erlaubte Typen: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Dateigröße prüfen
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            raise ValueError(
                f"Datei '{file.filename}' ist zu groß "
                f"({file_size / 1024 / 1024:.1f} MB > 7 MB)"
            )
        
        # Sichere Dateiname generieren (Timestamp + zufällig + Original)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ext = file.filename.rsplit('.', 1)[1].lower()
        
        # Originalnamen bereinigen
        original_name = secure_filename(file.filename.rsplit('.', 1)[0])[:20]
        
        # Finale Dateiname: 20251115_153045_inspection_photo.jpg
        safe_filename = f"{timestamp}_{original_name}.{ext}"
        
        file_path = os.path.join(upload_path, safe_filename)
        
        try:
            file.save(file_path)
            saved_filenames.append(safe_filename)
        except Exception as e:
            raise IOError(f"Fehler beim Speichern von '{file.filename}': {str(e)}")
    
    return saved_filenames


def delete_inspection_images(inspection_id) -> None:
    """Löscht alle Bilder einer Inspektion basierend auf der Inspektion selbst.
    
    Args:
        inspection_id: ID der Inspektion (wird in der DB lookup verwendet)
    """
    from models import db, Inspection, InspectionImage
    
    try:
        inspection = Inspection.query.get(inspection_id)
        if not inspection:
            return
        
        # Lösche alle InspectionImage-Einträge und deren Dateien
        for image in inspection.images:
            file_path = os.path.join(
                UPLOADS_DIR,
                inspection.date.strftime('%Y%m%d'),
                image.filename
            )
            
            # Datei löschen, falls sie existiert
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Warnung: Konnte Datei nicht löschen: {file_path} ({e})")
            
            # DB-Eintrag löschen (wird durch cascade=delete-orphan automatisch gelöscht)
            db.session.delete(image)
        
        db.session.commit()
        
        # Versuche, leere Ordner zu löschen
        date_dir = os.path.join(UPLOADS_DIR, inspection.date.strftime('%Y%m%d'))
        if os.path.exists(date_dir) and not os.listdir(date_dir):
            try:
                os.rmdir(date_dir)
            except Exception:
                pass  # Ordner ist nicht leer oder kann nicht gelöscht werden
    
    except Exception as e:
        print(f"Fehler beim Löschen von Inspektionsbildern: {str(e)}")


def cleanup_empty_date_directories() -> None:
    """Löscht leere Datums-Ordner aus dem Upload-Verzeichnis."""
    if not os.path.exists(UPLOADS_DIR):
        return
    
    try:
        for date_dir in os.listdir(UPLOADS_DIR):
            full_path = os.path.join(UPLOADS_DIR, date_dir)
            if os.path.isdir(full_path) and not os.listdir(full_path):
                os.rmdir(full_path)
    except Exception as e:
        print(f"Warnung: Fehler beim Aufräumen leerer Ordner: {e}")
