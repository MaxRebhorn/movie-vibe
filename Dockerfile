FROM python:3.11-slim

WORKDIR /app

# System-Dependencies für rapidfuzz, psycopg2 und netcat
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    gcc \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Installiere Python-Abhängigkeiten
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Restliches Projekt kopieren
COPY . .

# Einstiegspunkt setzen
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]