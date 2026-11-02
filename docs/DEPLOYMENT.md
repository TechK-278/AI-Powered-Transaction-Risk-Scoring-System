# Deployment Guide

This guide covers running the Transaction Risk Scoring System as containers on a single host with Docker Compose, and the settings to review before exposing it beyond a development machine.

## Topology

```
Browser ──► frontend (nginx :80, published as FRONTEND_PORT)
               ├── /            static React build
               └── /api/*  ──►  backend (Uvicorn :8000, internal only)
                                   ├── PostgreSQL (db :5432, internal only)
                                   └── ml/saved_models (read-only bind mount)
```

Only the frontend container publishes a port. The API and database are reachable solely on the Compose network. Because nginx proxies `/api`, the browser talks to a single origin and CORS is not involved in normal use.

## Prerequisites

1. Docker Engine 24+ with the Compose plugin.
2. Trained artifacts in `ml/saved_models/` (`fraud_model.joblib`, `preprocessor.joblib`, `model_metadata.json`). They are gitignored; produce them with the ML pipeline (see README) or copy them from your artifact store.
3. A `.env` file in the repository root, created from `.env.example`.

## Configuration

| Variable | Used by | Default | Notes |
|---|---|---|---|
| `POSTGRES_PASSWORD` | db, backend | — (required) | Use a long random value, e.g. `python -c "import secrets; print(secrets.token_urlsafe(24))"`. |
| `POSTGRES_USER` / `POSTGRES_DB` | db, backend | `risk_app` / `transaction_risk_db` | Compose builds `DATABASE_URL` from these. |
| `FRONTEND_PORT` | frontend | `8080` | Host port for the console. |
| `CORS_ORIGINS` | backend | `http://localhost:8080` | Only matters if browsers call the API on a different origin. |
| `UVICORN_WORKERS` | backend | `2` | Each worker loads its own copy of the model (~0.5 MB) and DB pool. |
| `LOG_LEVEL` | backend | `INFO` | Logs go to stdout; view with `docker compose logs backend`. |
| `RUN_MIGRATIONS` | backend | `true` | Set to `false` if migrations are run as a separate release step. |

`DEBUG` is forced to `false` in Compose, which also disables SQL echo logging.

## First deployment

```bash
cp .env.example .env            # edit POSTGRES_PASSWORD
docker compose up --build -d
docker compose ps               # all services should become "healthy"
curl -s http://localhost:8080/api/v1/health/
```

On start the backend entrypoint runs `alembic upgrade head` and then launches Uvicorn. Health checks:

- **backend**: `GET /api/v1/health/` from inside the container
- **frontend**: HTTP GET on `/`; starts only after the backend is healthy
- **db**: `pg_isready`

## Updating

| Change | Command |
|---|---|
| Application code | `git pull && docker compose up --build -d` |
| New model artifacts | Replace files in `ml/saved_models/`, then `docker compose restart backend` (artifacts are loaded once at startup) |
| Schema change | Add an Alembic revision; it is applied automatically on the next backend start |

Model artifacts are bind-mounted rather than baked into the image, so a retrained model can ship without rebuilding. Keep the scikit-learn and XGBoost versions in `backend/requirements.txt` aligned with the versions used for training; the artifacts are pickles and are version-sensitive.

## Backups

The database lives in the `postgres-data` named volume.

```bash
docker compose exec db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > backup_$(date +%F).sql
docker compose exec -T db psql -U "$POSTGRES_USER" "$POSTGRES_DB" < backup_YYYY-MM-DD.sql
```

## Production hardening checklist

Already in place:

- Containers run the API as a non-root user (`uid 10001`); artifacts are mounted read-only.
- API and database ports are not published to the host.
- nginx sends `X-Content-Type-Options`, `X-Frame-Options` and `Referrer-Policy`, hides its version, caps request bodies at 64 KB, and caches hashed assets immutably.
- Error responses never include stack traces or filesystem paths.
- Secrets come only from environment variables; `.env` files are excluded from images and Git.

Review before going live:

- **TLS.** Terminate HTTPS in front of the frontend container (a cloud load balancer, Caddy or Traefik) and only publish 443 on the edge.
- **Authentication.** The API has no authentication. Put it behind your SSO / identity-aware proxy, or add an auth layer, before exposing it to anyone outside the analyst team.
- **Rate limiting.** Add limits at the proxy for `POST /transactions/evaluate`.
- **Managed database.** For anything beyond a single host, point `DATABASE_URL` at a managed PostgreSQL instance with automated backups and remove the `db` service.
- **Image pinning.** Pin base images by digest and rebuild regularly for security patches.
- **Image size.** The `xgboost` wheel on Linux pulls in the NVIDIA NCCL library. The backend only runs CPU inference, so replacing it with `xgboost-cpu` (same version) in the image would cut several hundred MB; validate predictions against the current image before switching.

## Continuous integration

`.github/workflows/ci.yml` runs backend tests against a PostgreSQL service container (including the Alembic migration round trip), frontend tests and build, and builds both images. It does not publish images; add a registry push and deployment job once a target environment exists.
