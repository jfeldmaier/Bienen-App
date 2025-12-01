import os

# Setze ggf. den Namen deiner App-Datei hier:
FLASK_APP = "app.py"

def main():
    # Setze FLASK_APP-Umgebungsvariable
    os.environ["FLASK_APP"] = FLASK_APP

    # Frage nach dem Migrationstext
    msg = input("Bitte gib einen Beschreibungstext für die Migration ein: ")

    # Initialisiere Migration (nur beim ersten Mal nötig)
    if not os.path.exists("migrations"):
        os.system("flask db init")

    # Migration erzeugen
    os.system(f'flask db migrate -m "{msg}"')

    # Migration anwenden
    os.system("flask db upgrade")

    print("Migration abgeschlossen.")

if __name__ == "__main__":
    main()