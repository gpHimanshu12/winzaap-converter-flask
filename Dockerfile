FROM python:3.10-slim

# Install LibreOffice + fonts
RUN apt-get update && apt-get install -y \
    libreoffice \
    libreoffice-writer \
    libreoffice-impress \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# IMPORTANT: Railway injects PORT automatically
CMD gunicorn main:app --bind 0.0.0.0:$PORT --timeout 180
