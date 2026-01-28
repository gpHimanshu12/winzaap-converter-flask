from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import subprocess
import os
import uuid
import shutil

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "/tmp/uploads"
OUTPUT_FOLDER = "/tmp/outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "Winzaap Converter API is running"

@app.route("/health")
def health():
    return "OK", 200

@app.route("/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    libreoffice = shutil.which("libreoffice") or shutil.which("soffice")
    if not libreoffice:
        return jsonify({"error": "LibreOffice not available"}), 500

    file = request.files["file"]

    unique_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_{file.filename}")
    file.save(input_path)

    try:
        subprocess.run(
            [
                libreoffice,
                "--headless",
                "--nologo",
                "--nofirststartwizard",
                "--convert-to", "pdf",
                "--outdir", OUTPUT_FOLDER,
                input_path
            ],
            check=True,
            timeout=120
        )

        pdf_path = os.path.join(
            OUTPUT_FOLDER,
            os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
        )

        if not os.path.exists(pdf_path):
            return jsonify({"error": "PDF not generated"}), 500

        response = send_file(pdf_path, as_attachment=True)

        return response

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Conversion timeout"}), 504

    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Conversion failed"}), 500

    finally:
        # 🔥 CLEANUP (very important)
        try:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        except Exception:
            pass
