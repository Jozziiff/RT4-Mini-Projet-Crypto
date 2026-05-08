from flask import Flask
from routes.upload import upload_bp
from routes.download import download_bp
import os
from config import UPLOAD_FOLDER
from services.url_service import build_signed_url

app = Flask(__name__)
app.json.ensure_ascii = False
#  Limitation taille (5 MB)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# enregistrer les routes
app.register_blueprint(upload_bp)
app.register_blueprint(download_bp)

# route simple pour éviter 404
@app.route('/')

def home():
    return "API de partage sécurisé de fichiers"

@app.route("/generate-link/<path:filename>")
def generate_link(filename):

    signed_url = build_signed_url(
        "http://127.0.0.1:5000",
        filename
    )

    return {
        "signed_url": signed_url
    }

# créer le dossier storage automatiquement
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# lancer le serveur
if __name__ == "__main__":
    print("Serveur en cours de démarrage...")
    app.run(debug=True)