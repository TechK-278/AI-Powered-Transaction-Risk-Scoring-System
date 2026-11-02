#!/bin/sh
# Apply database migrations, then start the API server.
set -eu

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
    echo "Applying database migrations..."
    alembic upgrade head
fi

echo "Starting API on ${HOST}:${PORT} with ${UVICORN_WORKERS} worker(s)..."
exec uvicorn app.main:app \
    --host "${HOST}" \
    --port "${PORT}" \
    --workers "${UVICORN_WORKERS}" \
    --proxy-headers \
    --forwarded-allow-ips "*"
