# API Specifications

## Base Configuration
* **Base URL:** `http://localhost:8000`
* **API Prefix:** `/api/v1`
* **Interactive Documentation:** Swagger UI at `/docs`, ReDoc at `/redoc`

---

## Endpoints

### 1. Health Check
* **Route:** `GET /api/v1/health/`
* **Status:** Implemented
* **Tags:** `["Health"]`
* **Description:** Verifies service availability and returns basic application metadata.

#### Response (200 OK)
```json
{
  "status": "healthy",
  "service": "AI Transaction Risk Scoring System",
  "version": "1.0.0"
}
```

---

### 2. Transaction Risk Evaluation
* **Route:** `POST /api/v1/transactions/evaluate`
* **Status:** Implemented (Phase 8)
* **Tags:** `["Transactions"]`
* **Description:** Ingests transaction attributes, executes online feature preprocessing, generates fraud probability via loaded XGBoost model, applies Phase 7 `RiskScoreEngine`, and returns structured risk evaluation.
* **Note on Persistence:** Transactions are evaluated in real time without database persistence in Phase 8 (PostgreSQL persistence deferred to Phase 9).

#### Request Payload (`TransactionEvaluationRequest`)
```json
{
  "amount": 149.50,
  "time": 3600.0,
  "v1": 0.123,
  "v2": -0.456,
  "v3": 0.789,
  "v4": -0.321,
  "v14": -1.250,
  "v17": -2.100
}
```
*Note: `amount` (gt=0) is required. `time` (ge=0, default 0.0) and PCA features `v1`–`v28` (default 0.0) are accepted and mapped to model inputs.*

#### Response Payload (`TransactionEvaluationResponse` - 200 OK)
```json
{
  "fraud_probability": 0.735,
  "risk_score": 74,
  "risk_label": "High"
}
```

#### Status Codes
* **200 OK:** Successful risk evaluation.
* **400 Bad Request:** Numerical preprocessing or calculation error.
* **422 Unprocessable Entity:** Schema validation error (e.g. negative or missing amount).
* **503 Service Unavailable:** Inference artifacts missing or loading failure.
* **500 Internal Server Error:** Unexpected server-side failure.

---

### 3. Transaction History (Planned)
* **Route:** `GET /api/v1/transactions/`
* **Status:** `TODO — Not yet defined`
* **Description:** Retrieve paginated historical transaction risk assessments.

---

### 4. Transaction Details (Planned)
* **Route:** `GET /api/v1/transactions/{transaction_id}`
* **Status:** `TODO — Not yet defined`
* **Description:** Retrieve details and risk breakdown for a single transaction.

---

### 5. Analytics & Aggregates (Planned)
* **Route:** `GET /api/v1/analytics/summary`
* **Status:** `TODO — Not yet defined`
* **Description:** Summary metrics for dashboard KPI cards (total volume, flagged fraud rate, average risk score).
