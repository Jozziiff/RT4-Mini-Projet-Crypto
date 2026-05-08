from flask import Blueprint, send_file, jsonify, request
import os

from config import UPLOAD_FOLDER
from services.crypto_service import verify_signature
from services.url_service import parse_signed_url_params

download_bp = Blueprint("download", __name__)


@download_bp.route("/download", methods=["GET"])
def download_file():

    # Extraction sécurisée des paramètres
    filename, expires, signature = parse_signed_url_params(request.args)

    # Vérifier présence et validité des paramètres
    if not filename or not expires or not signature:
        return jsonify({
            "error": "URL invalide ou paramètres manquants"
        }), 400

    # Vérification cryptographique
    is_valid = verify_signature(
        filename,
        expires,
        signature
    )

    # Refus accès si signature invalide ou expirée
    if not is_valid:
        return jsonify({
            "error": "Signature invalide ou lien expiré"
        }), 403

    # Construction chemin sécurisé
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # Vérifier existence fichier
    if not os.path.exists(filepath):
        return jsonify({
            "error": "Fichier introuvable"
        }), 404

    # Téléchargement sécurisé
    return send_file(
        filepath,
        as_attachment=True
    )