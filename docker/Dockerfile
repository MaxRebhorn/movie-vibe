# Stage 1: Builder with BuildKit caching
FROM python:3.11-slim as builder

ARG REQUIREMENTS=requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements.txt
COPY requirements-test.txt requirements-test.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user --no-cache-dir -r ${REQUIREMENTS}

RUN --mount=type=cache,target=/root/.cache \
    python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Stage 2: Runtime
FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /root/.local /root/.local

COPY . .

ENV PATH=/root/.local/bin:$PATH \
    TRANSFORMERS_CACHE=/cache/transformers \
    SENTENCE_TRANSFORMERS_HOME=/cache/transformers \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN mkdir -p /cache/transformers && chmod 777 /cache

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
