from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import subprocess
import os
import uuid
import shutil

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

LIBREOFFICE_PATH = shutil.which("libreoffice") or shutil.which("soffice")

if not LIBREOFFICE_PATH:
    raise RuntimeError("LibreOffice not found")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "Winzaap Converter API is running"

@app.route("/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400

    file = request.files["file"]

    filename = f"{uuid.uuid4()}_{file.filename}"
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    try:
        subprocess.run(
            [
                LIBREOFFICE_PATH,
                "--headless",
                "--nologo",
                "--nofirststartwizard",
                "--convert-to", "pdf",
                input_path,
                "--outdir", OUTPUT_FOLDER
            ],
            check=True,
            timeout=150
        )

        pdf_path = os.path.join(
            OUTPUT_FOLDER,
            os.path.splitext(filename)[0] + ".pdf"
        )

        if not os.path.exists(pdf_path):
            return jsonify({"error": "PDF not generated"}), 500

        return send_file(pdf_path, as_attachment=True)

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Conversion timeout"}), 504

    except subprocess.CalledProcessError:
        return jsonify({"error": "Conversion failed"}), 500
