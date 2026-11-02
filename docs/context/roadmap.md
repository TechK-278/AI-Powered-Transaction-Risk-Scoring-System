# Project Roadmap & Milestones

The project is built incrementally across 14 structured phases.

| Phase | Milestone Name | Status | Description |
| :---: | :--- | :---: | :--- |
| **01** | **Planning & Architecture** | ✅ Completed | High-level system design, technology stack selection, and documentation. |
| **02** | **Folder Structure & Scaffolding** | ✅ Completed | Backend, frontend, ML, docs, and test directory hierarchy creation. |
| **03** | **Project Setup & Health API** | ✅ Completed | FastAPI initialization, Pydantic settings, logging, and `GET /api/v1/health/`. |
| **04** | **Dataset Selection & EDA** | ✅ Completed | Acquire fraud dataset, exploratory data analysis, class imbalance analysis. |
| **05** | **Data Preprocessing & Feature Engineering**| ✅ Completed | Cleaning pipelines, encoders, feature transformations, train/test split. |
| **06** | **Model Training & Evaluation** | ✅ Completed | XGBoost training, hyperparameter tuning, ROC-AUC / PR-AUC assessment. |
| **07** | **Risk Score Engine** | ✅ Completed | Probability calibration, 0–100 risk score transformation, risk categorization. |
| **08** | **FastAPI Backend Expansion** | ✅ Completed | Prediction API routes (`POST /api/v1/transactions/evaluate`), Pydantic validation schemas, ML loader & predictor service. |
| **09** | **PostgreSQL Integration & Alembic** | ✅ Completed | SQLAlchemy 2.0 Transaction model, Alembic migrations, persistence, history & detail APIs. |
| **10** | **React Frontend Development** | ✅ Completed | Vite setup, Tailwind design system, transaction submission form. |
| **11** | **Dashboard & Analytics** | ⏳ Pending | Recharts integration, risk distribution charts, transaction history table. |
| **12** | **Testing & Validation** | ⏳ Pending | Pytest unit tests, integration tests for API & ML inference pipeline. |
| **13** | **Dockerization** | ⏳ Pending | Dockerfile for backend/frontend, multi-service `docker-compose.yml`. |
| **14** | **Production Deployment** | ⏳ Pending | Production environment hardening, CI/CD pipeline, final documentation. |
