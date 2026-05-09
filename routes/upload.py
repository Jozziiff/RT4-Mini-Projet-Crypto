from flask import Blueprint, request, jsonify, render_template  # ← ajoute render_template
from services.file_service import save_file
from services.url_service import build_signed_url  # ← ajoute cet import

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier envoyé"}), 400

    file = request.files['file']
    filename, error = save_file(file)

    if error:
        return jsonify({"error": error}), 400

  
    signed_url = build_signed_url("http://127.0.0.1:5000", filename)
    return render_template('success.html', filename=filename, signed_url=signed_url)