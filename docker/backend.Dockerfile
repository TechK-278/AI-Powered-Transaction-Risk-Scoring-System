# FastAPI backend with ML inference.
# Build context: repository root (the image needs backend/ and ml/src/).

FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# libgomp is required by XGBoost for OpenMP threading.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt backend/requirements.txt
RUN pip install -r backend/requirements.txt

# Application code. ml/src is required to unpickle the fitted preprocessor
# (it references ml.src.preprocessing.feature_engineering).
COPY backend/app backend/app
COPY backend/alembic backend/alembic
COPY backend/alembic.ini backend/alembic.ini
COPY ml/src ml/src
COPY docker/backend-entrypoint.sh /usr/local/bin/backend-entrypoint.sh

# Trained artifacts are mounted at runtime (see docker-compose.yml) so a new
# model can be deployed without rebuilding the image.
RUN mkdir -p ml/saved_models \
    && chmod +x /usr/local/bin/backend-entrypoint.sh \
    && useradd --system --uid 10001 --no-create-home appuser \
    && chown -R appuser /app

USER appuser
WORKDIR /app/backend

ENV HOST=0.0.0.0 \
    PORT=8000 \
    UVICORN_WORKERS=2

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PORT\"]}/api/v1/health/', timeout=4)"

ENTRYPOINT ["backend-entrypoint.sh"]
