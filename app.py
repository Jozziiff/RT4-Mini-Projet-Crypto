from flask import Flask
from routes.upload import upload_bp
import os
from config import UPLOAD_FOLDER

app = Flask(__name__)

# 🔥 Limitation taille (5 MB)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# enregistrer la route upload
app.register_blueprint(upload_bp)

# route simple pour éviter 404
@app.route('/')
def home():
    return "API de partage sécurisé de fichiers"

# créer le dossier storage automatiquement
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# lancer le serveur
if __name__ == "__main__":
    print("Serveur en cours de démarrage...")
    app.run(debug=True)