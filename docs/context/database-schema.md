# Database Schema & Architecture

## Overview
* **Database Management System:** PostgreSQL
* **ORM:** SQLAlchemy 2.0 (Declarative Mapping with `Mapped` and `mapped_column`)
* **DB Driver:** `psycopg` (v3 binary)
* **Base Class:** `app.database.base.Base` (`DeclarativeBase`)
* **Migration Tool:** Alembic (Configured under `backend/alembic.ini` and `backend/alembic/`)

---

## Connection & Session Strategy
* **Engine:** Configured in `app.database.connection.engine` with `pool_pre_ping=True` and connection string loaded dynamically from `settings.database_url`.
* **Session Lifecycle:** Managed via generator dependency `app.database.session.get_db()`, yielding `SessionLocal` with explicit transaction rollback on error and guaranteed session closure in a `finally` block.

---

## Tables & Models

### Declarative Registry
All SQLAlchemy ORM models inherit from `app.database.base.Base`.

### Entity Models

#### 1. Transactions Table (`transactions`)
* **Model Class:** `app.models.transaction.Transaction`
* **Table Name:** `transactions`
* **Description:** Persists input transaction monetary values, temporal attributes, evaluated fraud probability, risk score, and categorical risk tier.

| Column | Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `VARCHAR(36)` | No | Primary Key, UUID4 string representation | Unique transaction identifier |
| `amount` | `FLOAT` | No | `CHECK (amount > 0)` | Evaluated monetary amount |
| `time` | `FLOAT` | No | Default `0.0`, `CHECK (time >= 0)` | Elapsed time in seconds from reference start |
| `fraud_probability` | `FLOAT` | No | `CHECK (fraud_probability >= 0.0 AND fraud_probability <= 1.0)` | Estimated posterior fraud probability |
| `risk_score` | `INTEGER` | No | `CHECK (risk_score >= 0 AND risk_score <= 100)` | Scaled risk score (0–100) |
| `risk_label` | `VARCHAR(20)` | No | Indexed | Modeled risk tier (`Low`, `Medium`, `High`) |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | No | `server_default=now()`, Indexed (DESC) | Record creation and evaluation timestamp |

**Indexes:**
* `ix_transactions_id` (`id`)
* `ix_transactions_risk_label` (`risk_label`)
* `ix_transactions_risk_score` (`risk_score`)
* `ix_transactions_created_at` (`created_at`)
* `ix_transactions_created_at_desc` (`created_at DESC`)

---

## Migration Strategy & Reversibility
* **Alembic Configuration:** `backend/alembic.ini`
* **Environment:** `backend/alembic/env.py` (dynamically resolves database URL from settings and registers `Base.metadata`)
* **Current Migrations:**
  * `0001_create_transactions`: Creates `transactions` table with full constraints, primary key, and indexes. Fully reversible via `downgrade()`.
