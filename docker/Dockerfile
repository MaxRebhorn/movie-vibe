# Dockerfile für Django
FROM python:3.11-slim

# Arbeitsverzeichnis setzen
WORKDIR /app

# System-Dependencies installieren
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Python Dependencies
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Projekt kopieren
COPY .. .

# Port freigeben
EXPOSE 8000

# Entrypoint Script
COPY ../entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]