from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import subprocess
import os
import uuid
import shutil
import sys

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def get_libreoffice_path():
    # macOS
    mac_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    if os.path.exists(mac_path):
        return mac_path

    # Linux / Docker
    return shutil.which("libreoffice") or shutil.which("soffice")

@app.route("/")
def home():
    return "Winzaap Converter API is running"

@app.route("/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    libreoffice = get_libreoffice_path()
    if not libreoffice:
        return jsonify({"error": "LibreOffice not found"}), 500

    file = request.files["file"]
    unique_id = str(uuid.uuid4())

    input_path = os.path.join(
        UPLOAD_FOLDER, f"{unique_id}_{file.filename}"
    )
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
                input_path,
            ],
            check=True,
            timeout=120,
        )

        pdf_name = os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
        pdf_path = os.path.join(OUTPUT_FOLDER, pdf_name)

        if not os.path.exists(pdf_path):
            return jsonify({"error": "PDF not generated"}), 500

        return send_file(pdf_path, as_attachment=True)

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Conversion timeout"}), 504

    except subprocess.CalledProcessError:
        return jsonify({"error": "Conversion failed"}), 500

    finally:
        # Cleanup
        try:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        except Exception:
            pass


if __name__ == "__main__":
    app.run(port=5000, debug=True)