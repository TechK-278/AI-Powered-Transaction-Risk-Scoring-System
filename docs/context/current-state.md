# Current Repository State

## Snapshot Date
* **Status:** Initial Development — Scaffolding & Context Layer Established

---

## Completed Components
1. **Repository Structure:**
   * Backend, ML, Frontend, Docker, Docs, and Tests hierarchies organized.
2. **FastAPI Foundation:**
   * Application entry point in `backend/app/main.py`.
   * Centralized configuration in `backend/app/core/config.py` using Pydantic Settings.
   * Centralized logging system in `backend/app/core/logging.py`.
   * Health check endpoint `GET /api/v1/health/` and response schema `HealthResponse` in `backend/app/schemas/health.py`.
3. **Database Foundation:**
   * SQLAlchemy 2.0 `Base` class declared in `backend/app/database/base.py`.
   * Database engine instantiation with `pool_pre_ping=True` and connection check in `backend/app/database/connection.py`.
   * Session generator dependency `get_db` configured in `backend/app/database/session.py`.
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

---

## Pending Components
1. **Machine Learning & Backend API (`backend/app/ml/`, `backend/app/api/`):**
   * Phase 08: FastAPI prediction endpoints, input validation schemas, inference pipeline (`loader.py`, `predictor.py`, `preprocessing.py`).
2. **Backend Persistence & Entities (`backend/app/`):**
   * Phase 09: PostgreSQL integration, SQLAlchemy ORM models, Alembic migrations.
   * SQLAlchemy ORM models in `backend/app/models/`.
   * Alembic migration environment and initial schema migrations.
   * Transaction evaluation and analytics API endpoints.
   * Custom exception handlers and input validators.
3. **Frontend Application (`frontend/`):**
   * Vite + React initialization and `package.json` setup.
   * Tailwind CSS design system setup.
   * Interactive dashboard, charts, and transaction risk scoring UI.
4. **DevOps & Testing (`docker/`, `tests/`):**
   * Pytest test suite for backend and ML components.
   * `Dockerfile` for backend and frontend.
   * Complete `docker-compose.yml` configuration.
