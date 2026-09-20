# System Architecture

## Overview
The **AI-Powered Transaction Risk Scoring System** is an end-to-end Machine Learning and web application designed to evaluate financial transactions in real time, predict fraud probability, and assign an actionable Risk Score (0–100).

```
                    +----------------------+
                    |    React Frontend    |
                    | (Vite, Tailwind CSS) |
                    +----------+-----------+
                               |
                        REST API Request
                               |
                               ▼
                    +----------------------+
                    |     FastAPI API      |
                    |    (/api/v1/...)     |
                    +----------+-----------+
                               |
                 Request Validation (Pydantic v2)
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

## System Components

### 1. Backend Layer (`backend/`)
* **Framework:** FastAPI (Python 3.11 / 3.13) with Uvicorn ASGI server.
* **Validation & Settings:** Pydantic v2 and `pydantic-settings`.
* **API Versioning:** Structured under `/api/v1/`.
* **Lifespan Management:** Structured startup/shutdown hooks via `asynccontextmanager`.
* **Logging:** Centralized Python logging with custom formatting (`LOG_FORMAT`, `DATE_FORMAT`).

### 2. Machine Learning Layer (`ml/` & `backend/app/ml/`)
* **Algorithm:** XGBoost classifier for tabular fraud prediction.
* **Supporting Libraries:** Scikit-learn, Pandas, NumPy, Joblib.
* **Offline Pipeline (`ml/`):** Data preprocessing, feature engineering, model training, evaluation, and artifact serialization.
* **Online Inference (`backend/app/ml/`):** Preprocessing transformers, model loader, prediction engine, and risk score calculator.

### 3. Database Layer (`backend/app/database/`)
* **Database Engine:** PostgreSQL.
* **ORM:** SQLAlchemy 2.0 with `psycopg` (v3) driver.
* **Session Pattern:** Scoped session dependency (`get_db`) with connection pooling and pre-ping validation.
* **Migrations:** Alembic (Planned).

### 4. Frontend Layer (`frontend/`)
* **Framework:** React with Vite.
* **Styling:** Tailwind CSS.
* **HTTP Client:** Axios.
* **Data Visualization:** Recharts.
* **Pages & Components:** Transaction evaluation form, risk distribution charts, alert panel, and transaction history table.

### 5. DevOps & Containerization (`docker/`, `docker-compose.yml`)
* **Containers:** Multi-container setup with FastAPI backend, React frontend, and PostgreSQL database.
* **Orchestration:** Docker Compose.
