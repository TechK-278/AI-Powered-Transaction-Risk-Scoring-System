# 💳 AI-Powered Transaction Risk Scoring System

> A production-ready end-to-end Machine Learning system that predicts the fraud risk of financial transactions using **XGBoost**, **FastAPI**, **React**, and **PostgreSQL**.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![React](https://img.shields.io/badge/React-Frontend-61DAFB)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

# 📖 Project Overview

Financial institutions process millions of transactions every day. Detecting fraudulent transactions accurately and in real time is one of the most important applications of Machine Learning in the fintech industry.

This project builds a complete **AI-Powered Transaction Risk Scoring System** that predicts the probability of fraud for a transaction and converts it into a meaningful **Risk Score (0–100)**.

The project follows industry-standard software engineering practices and demonstrates the complete Machine Learning lifecycle:

- Problem Understanding
- Data Collection
- Data Preprocessing
- Exploratory Data Analysis (EDA)
- Feature Engineering
- Model Training & Evaluation
- Risk Score Calculation
- Backend API Development
- Database Integration
- Frontend Dashboard
- Testing
- Dockerization
- Deployment

The repository was developed incrementally, phase by phase, to simulate a real-world software development workflow.

---

# 🎯 Objectives

- Build a production-quality fraud detection model
- Predict fraud probability for incoming transactions
- Convert predictions into a Risk Score
- Store transaction history in PostgreSQL
- Expose REST APIs using FastAPI
- Build an interactive React dashboard
- Containerize the application using Docker
- Deploy the complete system
- Follow clean architecture and engineering best practices

---

# ✨ Features

## Machine Learning

- Fraud Detection using XGBoost
- Data Preprocessing Pipeline
- Feature Engineering
- Model Evaluation
- Probability Prediction
- Risk Score Calculation

## Backend

- FastAPI REST API
- Request Validation
- Exception Handling
- Logging
- Swagger Documentation
- Modular Architecture

## Database

- PostgreSQL
- SQLAlchemy ORM
- Alembic Migrations
- Transaction History

## Frontend

- React
- Tailwind CSS
- Interactive Dashboard
- Charts & Analytics
- Responsive UI

## DevOps

- Docker
- Docker Compose
- GitHub Actions CI
- Environment Configuration

---

# 🛠️ Technology Stack

## Machine Learning

- Python
- Pandas
- NumPy
- Scikit-learn
- XGBoost
- Joblib

## Backend

- FastAPI
- Uvicorn
- SQLAlchemy
- Alembic
- Pydantic

## Database

- PostgreSQL

## Frontend

- React
- Vite
- Tailwind CSS
- Axios
- Recharts

## Testing

- Pytest
- HTTPX

## DevOps

- Docker
- Docker Compose
- Git
- GitHub

---

# 🏗️ High-Level System Architecture

```
                    +----------------------+
                    |    React Frontend    |
                    +----------+-----------+
                               |
                         REST API Request
                               |
                               ▼
                    +----------------------+
                    |      FastAPI API     |
                    +----------+-----------+
                               |
                 Request Validation (Pydantic)
                               |
                               ▼
                    Feature Engineering
                               |
                               ▼
                     XGBoost ML Model
                               |
                     Fraud Probability
                               |
                               ▼
                  Risk Score Calculation
                               |
                               ▼
                 PostgreSQL Database
                               |
                               ▼
                      JSON API Response
                               |
                               ▼
                    Analytics Dashboard
```

---

# 🔄 Project Workflow

```
Problem Definition
        │
        ▼
Dataset Collection
        │
        ▼
Data Cleaning
        │
        ▼
Exploratory Data Analysis (EDA)
        │
        ▼
Feature Engineering
        │
        ▼
Train/Test Split
        │
        ▼
Model Training
        │
        ▼
Model Evaluation
        │
        ▼
Model Selection
        │
        ▼
Model Serialization
        │
        ▼
FastAPI Backend
        │
        ▼
Risk Score Engine
        │
        ▼
PostgreSQL Storage
        │
        ▼
React Dashboard
        │
        ▼
Testing
        │
        ▼
Dockerization
        │
        ▼
Deployment
```

---

# 🤖 Machine Learning Pipeline

```
Raw Dataset
      │
      ▼
Data Cleaning
      │
      ▼
Missing Value Handling
      │
      ▼
Categorical Encoding
      │
      ▼
Feature Engineering
      │
      ▼
Train/Test Split
      │
      ▼
Model Training
      │
      ▼
Hyperparameter Tuning
      │
      ▼
Evaluation
      │
      ▼
Save Trained Model
      │
      ▼
FastAPI Inference
```

---

# 📊 Risk Score Logic

The trained Machine Learning model predicts the probability of fraud.

Example:

```
Fraud Probability = 0.91
```

Converted to:

```
Risk Score = 91
```

Risk Categories

| Score | Category |
|-------:|----------|
| 0–30 | 🟢 Low Risk |
| 31–70 | 🟡 Medium Risk |
| 71–100 | 🔴 High Risk |

---

# 📂 Project Structure

```text
.
├── backend/                     # FastAPI service
│   ├── alembic/                 # Database migrations
│   ├── app/
│   │   ├── api/                 # Routers: health, transactions, analytics
│   │   ├── core/                # Settings (pydantic-settings), logging
│   │   ├── database/            # Engine, session dependency, declarative base
│   │   ├── ml/                  # Model loader, online preprocessing, predictor, risk engine
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── repositories/        # Data access (transactions, analytics aggregates)
│   │   ├── schemas/             # Pydantic request/response models
│   │   ├── services/            # Analytics summary assembly
│   │   └── main.py
│   ├── requirements.txt         # Runtime dependencies
│   └── requirements-dev.txt     # + pytest, httpx
├── frontend/                    # React + Vite + Tailwind analyst console
│   ├── src/
│   │   ├── components/          # evaluation/, monitoring/, layout/, shared/
│   │   ├── domain/              # Risk tiers, payload building, formatters
│   │   ├── hooks/               # Data-fetching and state hooks
│   │   ├── pages/               # EvaluationPage, MonitoringPage
│   │   └── services/            # Axios API client and endpoint functions
│   └── tests/                   # node:test unit tests
├── ml/
│   ├── notebooks/               # EDA, preprocessing, training notebooks
│   ├── src/                     # Preprocessing + training pipelines
│   └── saved_models/            # Trained artifacts (gitignored)
├── tests/                       # Pytest suite
├── docker/                      # Dockerfiles, nginx template, entrypoint
├── docs/                        # Context docs, EDA report, deployment guide
├── .github/workflows/ci.yml     # CI: tests, frontend build, image builds
└── docker-compose.yml
```

---

# 🚀 Getting Started

## Prerequisites

- Python 3.13, Node.js 24, PostgreSQL 17 (or Docker)
- The [ULB Credit Card Fraud dataset](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) at `ml/data/raw/creditcard.csv` (only needed to retrain)

## 1. Produce the model artifacts

The trained artifacts are not committed. From the repository root:

```bash
python -m ml.src.preprocessing.pipeline   # writes ml/saved_models/preprocessor.joblib
python -m ml.src.training.train           # writes fraud_model.joblib and model_metadata.json
```

## 2. Run with Docker (recommended)

```bash
cp .env.example .env        # set POSTGRES_PASSWORD
docker compose up --build
```

Open **http://localhost:8080**. Compose starts PostgreSQL, applies Alembic migrations, starts the API (2 Uvicorn workers) and serves the frontend through nginx, which proxies `/api` to the backend. See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) for production notes.

## 3. Run locally for development

```bash
# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows  (source .venv/bin/activate on Linux/macOS)
pip install -r requirements-dev.txt
cp .env.example .env            # set DATABASE_URL
alembic upgrade head
uvicorn app.main:app --reload   # http://localhost:8000/docs

# Frontend (second terminal)
cd frontend
npm install
npm run dev                     # http://localhost:5173 (proxies /api to :8000)
```

---

# 📡 API

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/api/v1/health/` | Liveness check |
| `POST` | `/api/v1/transactions/evaluate` | Score a transaction and persist the assessment |
| `GET` | `/api/v1/transactions/` | Paginated history; filter by `risk_label`, `min_risk_score`, `max_risk_score` |
| `GET` | `/api/v1/transactions/{id}` | One persisted assessment |
| `GET` | `/api/v1/analytics/summary` | Totals, tier counts, score distribution, daily volume (`window_days` 1–90) |

### Example

```bash
curl -X POST http://localhost:8000/api/v1/transactions/evaluate \
  -H "Content-Type: application/json" \
  -d '{"amount": 149.50, "time": 3600, "v4": 4.2, "v10": -5.1, "v12": -7.0, "v14": -8.3, "v17": -6.4}'
```

```json
{
  "id": "7ed71051-6d81-46fe-ad7b-9246acbe7b8f",
  "fraud_probability": 0.8938,
  "risk_score": 89,
  "risk_label": "High",
  "created_at": "2026-11-02T06:41:43.794575Z"
}
```

`v1`–`v28` are the dataset's anonymised PCA components and default to `0`. Full schemas: [`docs/context/api-spec.md`](docs/context/api-spec.md) or Swagger at `/docs`.

---

# 📈 Analyst Console

**Evaluate** — enter amount, time and PCA components (or paste a dataset CSV row) and get the risk score, tier and fraud probability with a position on the 0–100 tier scale.

**Monitor** — summary figures (evaluations, mean score, mean probability, tier mix), a risk score distribution histogram, daily evaluation volume by tier (7/14/30 days), a filterable and paginated evaluation history table, and record lookup by ID.

---

# 🧪 Testing

```bash
# Backend (from the repository root)
python -m pytest

# Opt-in PostgreSQL migration round trip (database name must contain "test")
RUN_POSTGRES_TESTS=1 DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/transaction_risk_test python -m pytest tests/test_postgres_migrations.py

# Frontend
cd frontend && npm test && npm run build
```

API tests run against an in-memory SQLite database, so the suite never touches your development database. Tests that need the trained model are skipped automatically when `ml/saved_models` is empty, which is how CI runs.

---

# 🔁 Continuous Integration

`.github/workflows/ci.yml` runs on every push to `main` and every pull request:

1. **Backend** — pytest against a PostgreSQL 17 service container, including the Alembic migration round trip
2. **Frontend** — `npm test` and a production build
3. **Docker** — builds the backend and frontend images

---

# 🗺️ Development Roadmap

| Phase | Status |
|--------|--------|
| ✅ Planning & Architecture | Completed |
| ✅ Folder Structure | Completed |
| ✅ Dataset Selection & EDA | Completed |
| ✅ Data Preprocessing & Feature Engineering | Completed |
| ✅ Model Training & Evaluation | Completed |
| ✅ Risk Score Engine | Completed |
| ✅ FastAPI Backend | Completed |
| ✅ PostgreSQL Integration | Completed |
| ✅ React Frontend | Completed |
| ✅ Dashboard & Analytics | Completed |
| ✅ Testing | Completed |
| ✅ Dockerization | Completed |
| ✅ CI & Deployment Guide | Completed |

---

# 🎓 Learning Outcomes

By completing this project, I will gain hands-on experience in:

- End-to-End Machine Learning
- Fraud Detection Systems
- Feature Engineering
- XGBoost
- REST API Development
- Backend Engineering
- Database Design
- React Development
- Docker
- Git & GitHub
- Production Deployment
- Software Architecture

---

# 🔮 Future Enhancements

- JWT Authentication
- Role-Based Access Control
- Explainable AI (SHAP)
- MLflow Experiment Tracking
- Real-Time Streaming Predictions
- Redis Caching
- Kafka Integration
- Kubernetes Deployment
- Model Monitoring
- Automated Model Retraining

---

# 📜 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

**Krushna Kachhadiya**

Computer Engineering Student

Building this project to learn production-grade AI/ML engineering, backend development, and modern software engineering practices.

---

# ⭐ Support

If you find this project helpful, consider giving it a ⭐ on GitHub.

---

> **This project is being developed step by step following industry-standard software engineering practices. Every phase—from planning and data preprocessing to deployment—is implemented with a focus on scalability, maintainability, clean architecture, and production readiness.**