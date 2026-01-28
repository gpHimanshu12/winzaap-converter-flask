FROM python:3.10-slim

# Install LibreOffice and dependencies
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

# Railway expects port 8080
EXPOSE 8080

# IMPORTANT: use shell form so $PORT works
CMD gunicorn main:app --bind 0.0.0.0:${PORT:-8080} --timeout 180
