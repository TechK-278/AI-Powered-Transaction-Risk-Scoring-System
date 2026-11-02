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

### 5. Analytics Summary
* **Route:** `GET /api/v1/analytics/summary`
* **Status:** Implemented (Phase 11)
* **Tags:** `["Analytics"]`
* **Description:** Aggregates all persisted evaluations into totals, averages, risk tier counts, a ten-range score distribution, and per-day volume by tier for the monitoring dashboard. Aggregation runs in the database (`GROUP BY` score and label); daily volume is bucketed by UTC day in the service layer so results do not depend on the database session time zone.

#### Query Parameters
* `window_days` (int, optional): Days of daily volume to return, including today (UTC). Default `14`, range `1–90`.

#### Response Payload (`AnalyticsSummaryResponse` - 200 OK)
```json
{
  "total_evaluations": 68,
  "average_risk_score": 19.34,
  "average_fraud_probability": 0.1938,
  "risk_label_counts": [
    {"risk_label": "Low", "count": 55},
    {"risk_label": "Medium", "count": 0},
    {"risk_label": "High", "count": 13}
  ],
  "score_distribution": [
    {"score_from": 0, "score_to": 9, "count": 53},
    {"score_from": 90, "score_to": 100, "count": 12}
  ],
  "daily_volume": [
    {"day": "2026-11-02", "low": 51, "medium": 0, "high": 13}
  ],
  "window_days": 14
}
```
`score_distribution` always contains ten ranges (0–9 … 90–100; abbreviated above). `daily_volume` contains one row per day in the window, oldest first, including days with no evaluations. Averages are `null` when no evaluations exist.

#### Status Codes
* **200 OK:** Summary computed.
* **422 Unprocessable Entity:** `window_days` outside 1–90.
* **500 Internal Server Error:** Database query failure.
