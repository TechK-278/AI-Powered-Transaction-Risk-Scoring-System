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

### 2. Transaction Risk Evaluation & Persistence
* **Route:** `POST /api/v1/transactions/evaluate`
* **Status:** Implemented (Phase 8 & 9)
* **Tags:** `["Transactions"]`
* **Description:** Ingests transaction attributes, executes online feature preprocessing, generates fraud probability via loaded XGBoost model, applies Phase 7 `RiskScoreEngine`, persists the assessment record in PostgreSQL, and returns structured risk evaluation.

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
  "id": "e4d909c2-9051-4e76-880c-a6a7cb8d598b",
  "fraud_probability": 0.735,
  "risk_score": 74,
  "risk_label": "High",
  "created_at": "2026-09-23T13:30:00.000Z"
}
```

#### Status Codes
* **200 OK:** Successful risk evaluation and database persistence.
* **400 Bad Request:** Numerical preprocessing or calculation error.
* **422 Unprocessable Entity:** Schema validation error (e.g. negative or missing amount).
* **503 Service Unavailable:** Inference artifacts missing or loading failure.
* **500 Internal Server Error:** Unexpected server-side or database persistence failure.

---

### 3. Transaction History & Filtered Listing
* **Route:** `GET /api/v1/transactions/`
* **Status:** Implemented (Phase 9)
* **Tags:** `["Transactions"]`
* **Description:** Retrieve paginated historical transaction risk assessments with optional risk tier and score filtering.

#### Query Parameters
* `page` (int, default=1, ge=1): Page number (1-indexed).
* `page_size` (int, default=20, ge=1, le=100): Items returned per page.
* `risk_label` (string, optional): Filter by risk tier (`Low`, `Medium`, `High`).
* `min_risk_score` (int, optional, 0-100): Minimum risk score (inclusive).
* `max_risk_score` (int, optional, 0-100): Maximum risk score (inclusive).

#### Response Payload (`PaginatedTransactionsResponse` - 200 OK)
```json
{
  "items": [
    {
      "id": "e4d909c2-9051-4e76-880c-a6a7cb8d598b",
      "amount": 149.50,
      "time": 3600.0,
      "fraud_probability": 0.735,
      "risk_score": 74,
      "risk_label": "High",
      "created_at": "2026-09-23T13:30:00.000Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

#### Status Codes
* **200 OK:** Successfully retrieved paginated records.
* **400 Bad Request:** Invalid filter criteria (e.g., `min_risk_score > max_risk_score`).
* **422 Unprocessable Entity:** Query parameter type validation error.
* **500 Internal Server Error:** Database query failure.

---

### 4. Transaction Details
* **Route:** `GET /api/v1/transactions/{transaction_id}`
* **Status:** Implemented (Phase 9)
* **Tags:** `["Transactions"]`
* **Description:** Retrieve full details for a single persisted transaction evaluation record.

#### Path Parameters
* `transaction_id` (string, UUID): Unique identifier of the transaction.

#### Response Payload (`TransactionDetailResponse` - 200 OK)
```json
{
  "id": "e4d909c2-9051-4e76-880c-a6a7cb8d598b",
  "amount": 149.50,
  "time": 3600.0,
  "fraud_probability": 0.735,
  "risk_score": 74,
  "risk_label": "High",
  "created_at": "2026-09-23T13:30:00.000Z"
}
```

#### Status Codes
* **200 OK:** Record found.
* **404 Not Found:** Transaction record with given ID does not exist.
* **500 Internal Server Error:** Database query failure.

---

### 5. Analytics & Aggregates (Planned)
* **Route:** `GET /api/v1/analytics/summary`
* **Status:** `TODO — Not yet defined`
* **Description:** Summary metrics for dashboard KPI cards (total volume, flagged fraud rate, average risk score).
