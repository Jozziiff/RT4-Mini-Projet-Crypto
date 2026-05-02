from flask import Blueprint, request, jsonify
from services.file_service import save_file

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier envoyé"}), 400

    file = request.files['file']

    filename, error = save_file(file)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({
        "message": "Fichier uploadé avec succès",
        "filename": filename
    }), 200