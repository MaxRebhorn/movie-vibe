# Stage 1: Builder
FROM python:3.11-slim as builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    netcat-openbsd \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

# Configure model cache
ENV PATH=/root/.local/bin:$PATH \
    TRANSFORMERS_CACHE=/app/.cache \
    SENTENCE_TRANSFORMERS_HOME=/app/.cache

RUN mkdir -p /app/.cache && chmod 777 /app/.cache

# FIX: Correct entrypoint path
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && \
    dos2unix /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]