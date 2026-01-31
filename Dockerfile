FROM python:3.12-slim AS builder

WORKDIR /app
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && python -m pip install --prefix=/install -r requirements.txt

COPY app ./app
COPY alembic.ini ./alembic.ini

FROM python:3.12-slim AS runtime

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=builder /install /usr/local
COPY app ./app
COPY frontend ./frontend
COPY alembic.ini ./alembic.ini

RUN useradd -m appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app/data
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/v1/health')"

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

FROM runtime AS test

USER root
COPY requirements.txt .
COPY requirements-dev.txt .
RUN python -m pip install --no-cache-dir -r requirements-dev.txt

COPY tests ./tests
COPY frontend ./frontend
COPY Dockerfile ./Dockerfile
COPY docker-compose.yml ./docker-compose.yml

USER appuser
