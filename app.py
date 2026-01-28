from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import subprocess
import os
import uuid

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

LIBREOFFICE_PATH = "/Applications/LibreOffice.app/Contents/MacOS/soffice"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ✅ Health check route
@app.route("/")
def home():
    return "Winzaap Converter API is running"

# ✅ Word / PPT → PDF
@app.route("/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    filename = f"{uuid.uuid4()}_{file.filename}"
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    try:
        subprocess.run(
            [
                LIBREOFFICE_PATH,
                "--headless",
                "--convert-to", "pdf",
                input_path,
                "--outdir", OUTPUT_FOLDER,
            ],
            check=True,
        )

        pdf_name = os.path.splitext(filename)[0] + ".pdf"
        pdf_path = os.path.join(OUTPUT_FOLDER, pdf_name)

        if not os.path.exists(pdf_path):
            return jsonify({"error": "PDF not generated"}), 500

        return send_file(pdf_path, as_attachment=True)

    except subprocess.CalledProcessError as e:
        print("LibreOffice error:", e)
        return jsonify({"error": "Conversion failed"}), 500


if __name__ == "__main__":
    app.run()
