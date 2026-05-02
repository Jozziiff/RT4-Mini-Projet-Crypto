import os
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    if not file:
        return None, "Aucun fichier fourni"

    if file.filename == "":
        return None, "Nom de fichier vide"

    filename = secure_filename(file.filename)

    #  Vérification du type de fichier
    if not allowed_file(filename):
        return None, "Type de fichier non autorisé"

    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # Vérifier si le fichier existe déjà
    if os.path.exists(filepath):
        return None, "Le fichier existe déjà"

    try:
        file.save(filepath)
    except Exception as e:
        return None, f"Erreur lors de la sauvegarde: {str(e)}"

    return filename, None