# System Requirements

## Functional Requirements

### 1. Real-Time Risk Scoring
* Accept incoming transaction payloads via REST API.
* Preprocess and extract engineered features in real time.
* Output a calibrated fraud probability ($P \in [0.0, 1.0]$).
* Map probability to a discrete **Risk Score (0–100)**.
* Classify transactions into risk tiers:
  * **Low Risk:** 0 – 30
  * **Medium Risk:** 31 – 70
  * **High Risk:** 71 – 100

### 2. Transaction Persistence
* Store evaluated transactions, predicted probabilities, risk scores, and decision metadata in PostgreSQL.
* Retrieve historical transactions with filtering and pagination.

### 3. Monitoring & Analytics Dashboard
* Display real-time risk scores and transaction evaluation results.
* Visualize risk distributions, fraudulent transaction rates, and high-risk alerts.
* Provide transaction lookup and detailed inspection views.

### 4. Health & Diagnostics
* Expose system health status, service identity, and version via `GET /api/v1/health/`.

## Non-Functional Requirements

### 1. Code Quality & Architecture
* Follow PEP8 naming conventions and style guides.
* Apply Clean Architecture principles: Strict separation between API routers, domain logic (services), persistence (database), and ML inference.
* Comprehensive type annotations and docstrings on all functions and modules.
* Zero circular dependencies.

### 2. Performance & Reliability
* Sub-second latency for online inference requests.
* Robust exception handling with clean client-facing JSON errors and structured server logs.
* Database connection pooling with keep-alive verification (`pool_pre_ping=True`).

### 3. Security Boundary
* Strict `.env` handling: Sensitive credentials must never be committed to version control.
* Input validation on all incoming request schemas via Pydantic.
* Safe error messages preventing stack trace exposure to external clients.

## Pending Specifications
* Specific rate limiting thresholds: `TODO — Not yet defined`
* Authentication mechanism (JWT / API Key / RBAC): `TODO — Not yet defined`
* Data retention policy: `TODO — Not yet defined`
