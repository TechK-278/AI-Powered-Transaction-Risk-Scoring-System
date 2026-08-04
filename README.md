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

This repository is being developed incrementally to simulate a real-world software development workflow.

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
- GitHub Actions (planned)
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
transaction-risk-scoring-system/
│
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── core/             # Configurations
│   │   ├── database/         # Database connection
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   ├── ml/               # ML model inference
│   │   ├── utils/            # Helper functions
│   │   └── main.py
│   └── requirements.txt
│
├── frontend/                 # React application
│   ├── public/
│   ├── src/
│   └── package.json
│
├── ml/                       # Machine Learning
│   ├── data/
│   ├── notebooks/
│   ├── preprocessing/
│   ├── training/
│   ├── evaluation/
│   └── saved_models/
│
├── tests/                    # Unit & Integration Tests
│
├── docker/                   # Docker configuration
│
├── docs/                     # Documentation
│   └── DEVELOPMENT_GUIDE.md
│
├── .github/
│
├── docker-compose.yml
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

# 🚀 Installation

## Clone the Repository

```bash
git clone https://github.com/<your-username>/transaction-risk-scoring-system.git

cd transaction-risk-scoring-system
```

---

## Backend Setup

```bash
cd backend

python -m venv venv
```

Activate virtual environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Frontend Setup

```bash
cd frontend

npm install
```

---

## Database Setup

Start PostgreSQL and configure the environment variables.

Example:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/transaction_db
```

---

# ▶️ Running the Application

## Start Backend

```bash
cd backend

uvicorn app.main:app --reload
```

Backend

```
http://localhost:8000
```

Swagger

```
http://localhost:8000/docs
```

ReDoc

```
http://localhost:8000/redoc
```

---

## Start Frontend

```bash
cd frontend

npm run dev
```

Frontend

```
http://localhost:5173
```

---

# 📡 API Example

## Request

```json
{
    "amount": 5400,
    "merchant": "Amazon",
    "country": "India",
    "hour": 22,
    "device": "Mobile"
}
```

---

## Response

```json
{
    "risk_score": 87,
    "fraud_probability": 0.87,
    "label": "High Risk"
}
```

---

# 📈 Dashboard

The React dashboard will provide:

- Transaction Prediction
- Risk Score Visualization
- Fraud Probability
- Transaction History
- High-Risk Alerts
- Analytics Charts
- Summary Cards
- Risk Distribution
- Recent Transactions

---

# 🧪 Testing

The project will include:

- Unit Tests
- API Tests
- Model Validation Tests
- Integration Tests

Run all tests:

```bash
pytest
```

---

# 🐳 Docker Support

The application will be fully containerized.

Run the entire application using Docker Compose.

```bash
docker compose up --build
```

This starts:

- FastAPI Backend
- React Frontend
- PostgreSQL Database

---

# ☁️ Deployment

The project is designed for production deployment.

Deployment targets include:

- Backend
- Frontend
- PostgreSQL
- Docker Containers

Deployment configuration will be added during the final phase of the project.

---

# 🗺️ Development Roadmap

The project is being built incrementally following industry best practices.

| Phase | Status |
|--------|--------|
| ✅ Planning & Architecture | Completed |
| ⬜ Folder Structure | Pending |
| ⬜ Dataset Selection | Pending |
| ⬜ Data Preprocessing | Pending |
| ⬜ Exploratory Data Analysis | Pending |
| ⬜ Feature Engineering | Pending |
| ⬜ Model Training | Pending |
| ⬜ Risk Score Engine | Pending |
| ⬜ FastAPI Backend | Pending |
| ⬜ PostgreSQL Integration | Pending |
| ⬜ React Frontend | Pending |
| ⬜ Dashboard & Analytics | Pending |
| ⬜ Testing | Pending |
| ⬜ Dockerization | Pending |
| ⬜ Deployment | Pending |
| ⬜ Final Documentation | Pending |

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