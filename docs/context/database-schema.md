# Database Schema & Architecture

## Overview
* **Database Management System:** PostgreSQL
* **ORM:** SQLAlchemy 2.0 (Declarative Mapping)
* **DB Driver:** `psycopg` (v3 binary)
* **Base Class:** `app.database.base.Base` (`DeclarativeBase`)
* **Migration Tool:** Alembic (Planned)

---

## Connection & Session Strategy
* **Engine:** Configured in `app.database.connection.engine` with `pool_pre_ping=True` and connection string loaded from `settings.database_url`.
* **Session Lifecycle:** Managed via generator dependency `app.database.session.get_db()`, yielding `SessionLocal` and guaranteeing session closure in a `finally` block.

---

## Tables & Models

### Declarative Registry
All SQLAlchemy ORM models inherit from `app.database.base.Base`.

### Planned Entity Models
1. **Transactions Table (`transactions`):**
   * Fields: `TODO — Not yet defined`
   * Target Schema (indicative):
     * `id` (UUID / Integer, Primary Key)
     * `transaction_time` (DateTime / Timestamp)
     * `amount` (Numeric / Float)
     * `merchant` (String)
     * `country` (String)
     * `device` (String)
     * `fraud_probability` (Float)
     * `risk_score` (Integer)
     * `risk_label` (String: LOW, MEDIUM, HIGH)
     * `created_at` (DateTime with timezone)

2. **Audit / Log Table (Optional):**
   * Fields: `TODO — Not yet defined`

3. **Relationships & Foreign Keys:**
   * Relationships: `TODO — Not yet defined`

---

## Migration Strategy
* Alembic initialization and autogeneration will be configured once the transaction entities are formally defined in `app/models/`.
