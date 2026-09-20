# Architecture Decision Records (ADR)

## ADR-001: Clean Architecture & Separation of Concerns
* **Status:** Accepted
* **Context:** The system needs to be maintainable, scalable, easily testable, and suitable for interview discussions.
* **Decision:** Enforce strict separation between API routing (`app/api`), application/business logic (`app/services`), data persistence (`app/database`, `app/models`), schemas (`app/schemas`), and machine learning inference (`app/ml`).
* **Consequence:** Modules remain decoupled; changing the database or ML model implementation does not require breaking API endpoints.

---

## ADR-002: Backend Framework Selection (FastAPI + Pydantic v2)
* **Status:** Accepted
* **Context:** Financial fraud scoring requires low inference latency, automatic request validation, and OpenAPI documentation.
* **Decision:** Use FastAPI with Pydantic v2 and `pydantic-settings`.
* **Consequence:** Fast async execution, automatic OpenAPI schema generation, compile-time and runtime type safety.

---

## ADR-003: Database & ORM Selection (PostgreSQL + SQLAlchemy 2.0)
* **Status:** Accepted
* **Context:** Need ACID-compliant relational storage for transaction logs, risk decisions, and analytics queries.
* **Decision:** Use PostgreSQL with SQLAlchemy 2.0 DeclarativeBase and `psycopg` (v3) driver.
* **Consequence:** Standardized relational modeling, robust connection pooling, and seamless future migration support via Alembic.

---

## ADR-004: Core Machine Learning Algorithm (XGBoost)
* **Status:** Accepted
* **Context:** Fraud detection in tabular financial datasets is characterized by non-linear interactions, mixed data types, and extreme class imbalance.
* **Decision:** Select XGBoost as the primary tabular classification model.
* **Consequence:** High predictive performance on tabular data, built-in support for missing values, and efficient inference capability.

---

## ADR-005: Read-Only Shared Context Protocol
* **Status:** Accepted
* **Context:** Antigravity and external analysis tools (such as ChatGPT) require synchronized, verified project context without compromising security or exposing `.env` files.
* **Decision:** Standardize project context into structured markdown files (`docs/context/*.md`) exposed via a local read-only stdio MCP server.
* **Consequence:** Antigravity and external tools read from a single source of truth without granting write access or network/credential exposure.
