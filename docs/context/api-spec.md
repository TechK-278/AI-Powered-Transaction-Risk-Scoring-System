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

### 2. Transaction Risk Evaluation (Planned)
* **Route:** `POST /api/v1/transactions/evaluate` (or `POST /api/v1/predict`)
* **Status:** `TODO — Not yet defined`
* **Description:** Ingests transaction attributes, executes ML feature extraction and model inference, computes risk score, saves record to database, and returns scoring breakdown.

#### Example Request Payload
```json
{
  "amount": 5400.00,
  "merchant": "Amazon",
  "country": "India",
  "hour": 22,
  "device": "Mobile"
}
```

#### Example Response Payload
```json
{
  "risk_score": 87,
  "fraud_probability": 0.87,
  "label": "High Risk"
}
```

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
