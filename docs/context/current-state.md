# Current Repository State

## Snapshot Date
* **Status:** All 14 phases completed (2026-11-02)

---

## Completed Components
1. **Repository Structure:**
   * Backend, ML, Frontend, Docker, Docs, and Tests hierarchies organized.
2. **FastAPI Foundation:**
   * Application entry point in `backend/app/main.py`.
   * Centralized configuration in `backend/app/core/config.py` using Pydantic Settings with robust `.env` resolution.
   * Centralized logging system in `backend/app/core/logging.py`.
   * Health check endpoint `GET /api/v1/health/` and response schema `HealthResponse` in `backend/app/schemas/health.py`.
3. **Database Foundation & PostgreSQL Persistence (Phase 9):**
   * SQLAlchemy 2.0 `Base` class declared in `backend/app/database/base.py`.
   * Database engine instantiation with `pool_pre_ping=True` in `backend/app/database/connection.py`.
   * Session generator dependency `get_db` configured in `backend/app/database/session.py`.
   * SQLAlchemy 2.0 `Transaction` ORM model in `backend/app/models/transaction.py` with full constraints and indexes.
   * Clean `TransactionRepository` data access layer in `backend/app/repositories/transaction.py`.
   * Configured Alembic migrations in `backend/alembic.ini` and `backend/alembic/env.py` with reversible `0001_create_transactions` initial migration.
   * Transaction evaluation persistence in `POST /api/v1/transactions/evaluate`.
   * Historical transaction listing with pagination and filters in `GET /api/v1/transactions/`.
   * Transaction detail lookup in `GET /api/v1/transactions/{transaction_id}`.
4. **Context Layer:**
   * Structured documentation in `docs/context/` covering architecture, requirements, API specs, database schemas, ML pipeline, decisions, roadmap, and state.
   * Local read-only MCP server designed for secure stdio context querying.
5. **Dataset Selection & EDA (Phase 4):**
   * ULB Credit Card Fraud dataset acquired and verified under `ml/data/raw/creditcard.csv`.
   * Complete EDA notebook implemented and executed under `ml/notebooks/01_dataset_eda.ipynb`.
   * Data Quality and EDA Report generated in `docs/eda-report.md`.
6. **Data Preprocessing & Feature Engineering (Phase 5):**
   * Modular preprocessing package created under `ml/src/` (`config.py`, `data_cleaning.py`, `feature_engineering.py`, `pipeline.py`).
   * Cleaned dataset and resolved 1,081 duplicate records.
   * Generated stratified 70/15/15 train/val/test splits with zero leakage.
   * Engineered cyclic temporal features (`hour_sin`, `hour_cos`) and scaled log amount (`amount_log`).
   * Serialized fitted `preprocessor.joblib` artifact.
   * Complete reproducible preprocessing notebook in `ml/notebooks/02_preprocessing.ipynb`.
   * Comprehensive unit and integration test suite in `tests/test_preprocessing.py`.
7. **Model Training & Evaluation (Phase 6):**
   * Modular training package created under `ml/src/training/` (`train.py`, `evaluate.py`, `metrics.py`).
   * Trained `xgboost.XGBClassifier` with dynamically calculated `scale_pos_weight = 599.02`.
   * Performed threshold optimization on validation set to maximize F1-score (optimal threshold = 0.95).
   * Verified generalization on 42,559 test transactions: PR-AUC = 0.7761, ROC-AUC = 0.9656, F1 = 0.8029, Precision = 83.33%, Recall = 77.46%.
   * Exported serialized model artifact `fraud_model.joblib` and `model_metadata.json`.
   * Executed reproducible training notebook `ml/notebooks/03_model_training.ipynb`.
   * Comprehensive unit & integration tests in `tests/test_training.py`.
8. **Risk Score Engine (Phase 7):**
   * Implemented standalone, constant-time `RiskScoreEngine` and `RiskAssessment` in `backend/app/ml/risk_engine.py`.
   * Maps fraud probability $P(\text{Class}=1) \in [0.0, 1.0]$ into normalized 0–100 integer scores using standard half-up rounding.
   * Categorizes scores into Low (0–30: Lower modeled fraud risk), Medium (31–70: Moderate modeled fraud risk), and High (71–100: Higher modeled fraud risk).
   * Downstream transaction policies and operational actions remain explicitly outside Phase 7 scope.
   * Enforces strict monotonicity and validates numerical bounds, rejecting NaNs, infinities, and invalid inputs.
   * Fully verified with comprehensive unit tests in `tests/test_risk_engine.py`.
9. **FastAPI Backend Expansion (Phase 8):**
   * Real-time risk scoring endpoint `POST /api/v1/transactions/evaluate` implemented in `backend/app/api/transactions.py`.
   * Pydantic v2 request (`TransactionEvaluationRequest`) and response (`TransactionEvaluationResponse`) schemas in `backend/app/schemas/transaction.py`.
   * Singleton model and preprocessor artifact manager `ModelLoader` in `backend/app/ml/loader.py`.
   * Online inference feature transformer `OnlineFeaturePreprocessor` in `backend/app/ml/preprocessing.py`.
   * End-to-end prediction coordinator `TransactionPredictor` in `backend/app/ml/predictor.py`.
   * Safe exception handling without stack trace or filesystem path exposure.
   * Comprehensive unit and integration test suite in `tests/test_transactions_api.py`.

---

10. **React Frontend (Phase 10):**
   * Vite + React 19 + Tailwind CSS v4 analyst console in `frontend/` with a neutral enterprise theme defined as tokens in `src/index.css`.
   * Layered structure: `services/` (Axios client, endpoint functions, error mapping), `domain/` (risk tiers, payload building, formatters), `hooks/`, `components/`, `pages/`.
   * Evaluate workspace: `TransactionInputForm` (validation, PCA grid, dataset CSV row import) and `RiskScorePanel` (score, tier, probability, 0–100 tier scale).
   * Configurable backend CORS via `CORS_ORIGINS`; Vite dev server proxies `/api` to the backend.
11. **Dashboard & Analytics (Phase 11):**
   * `GET /api/v1/analytics/summary` (`api/analytics.py`, `repositories/analytics.py`, `services/analytics_service.py`, `schemas/analytics.py`).
   * Monitor workspace: `TransactionSummary`, `RiskDistributionChart`, `DailyEvaluationVolumeChart` (Recharts, CVD-validated tier colors), `PredictionHistoryTable` with filters and pagination, `RecordLookupForm`, `TransactionDetailPanel`. Lazy-loaded to keep the evaluate bundle small.
12. **Testing & Validation (Phase 12):**
   * `tests/conftest.py` routes every test to an isolated in-memory SQLite database; model-dependent tests skip when artifacts are absent.
   * API integration tests with a stubbed predictor (`tests/test_api_integration.py`), analytics tests, and an opt-in Alembic round trip on PostgreSQL guarded to `*test*` databases.
   * Frontend domain tests with the built-in Node test runner (`npm test`).
13. **Dockerization (Phase 13):**
   * `docker/backend.Dockerfile` (non-root, healthcheck, migrations on start), `docker/frontend.Dockerfile` (nginx with `/api` proxy and security headers), `docker-compose.yml` with health-gated startup and read-only artifact mount.
14. **CI & Deployment (Phase 14):**
   * `.github/workflows/ci.yml`: backend tests against a PostgreSQL service, frontend tests and build, image builds.
   * `docs/DEPLOYMENT.md`: configuration, operations, backups, and production hardening checklist. README rewritten with accurate setup instructions.

---

## Known Limitations / Next Steps
* The API has no authentication or rate limiting; see the hardening checklist in `docs/DEPLOYMENT.md`.
* Transaction endpoints in `api/transactions.py` are `async def` but call blocking DB and model code; converting them to plain `def` would let FastAPI run them in its threadpool under load.
* Trained artifacts are not versioned in a registry; CI skips model-dependent tests.
* The backend image includes the NVIDIA NCCL library pulled in by `xgboost`; `xgboost-cpu` would shrink it.
