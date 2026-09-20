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

---

## ADR-006: Preprocessing, Feature Engineering & Leakage Prevention Strategy
* **Status:** Accepted
* **Context:** High-consequence financial fraud detection requires absolute prevention of data leakage between training, validation, and testing partitions. Furthermore, online inference requires exact parity with offline training feature transformations.
* **Decision:**
  1. Remove duplicate records (1,081 rows) prior to splitting to prevent exact observation leakage between partitions.
  2. Use a fixed 70/15/15 Stratified Split (`stratify=y`, seed=42) preserving minority fraud proportion (0.1668%).
  3. Transform elapsed seconds into 24-hour continuous trigonometric coordinates (`hour_sin`, `hour_cos`) and drop raw `Time` to prevent temporal epoch overfitting.
  4. Apply $\log(1 + \text{Amount})$ with Scikit-learn `RobustScaler` fitted **exclusively** on the training partition (`X_train`).
  5. Encapsulate all feature transformations inside a serializable Scikit-learn transformer (`TransactionFeatureTransformer`) exported via `joblib` for both batch model training and online single-transaction FastAPI evaluation.
  6. Defer class re-weighting / sampling techniques to Phase 06 model optimization.
* **Consequence:** 100% deterministic transformation parity between offline experimentation and online real-time inference with zero data leakage.

---

## ADR-007: XGBoost Model Configuration, Dynamic Class Weighting & Threshold Optimization
* **Status:** Accepted
* **Context:** Financial fraud detection features severe class imbalance (~599:1). Unweighted models exhibit poor fraud recall, while uncalibrated probability thresholds lead to unacceptable false alarm rates in high-throughput banking systems.
* **Decision:**
  1. Train `xgboost.XGBClassifier` with histogram tree method (`tree_method='hist'`), 200 estimators, depth 5, learning rate 0.05, and L1/L2 regularization (`reg_alpha=0.1`, `reg_lambda=1.0`).
  2. Dynamically calculate `scale_pos_weight = N_neg / N_pos = 599.02` from training labels, avoiding artificial synthetic data generation (SMOTE) and preserving natural feature relationships.
  3. Perform a systematic decision threshold sweep on the **Validation Set** to find the threshold maximizing $F_1$-score ($\text{threshold} = 0.95$).
  4. Evaluate generalization on the untouched test partition using PR-AUC (Average Precision), F1, Recall, and Precision rather than raw classification accuracy.
  5. Export serialized model (`fraud_model.joblib`) and structured metadata record (`model_metadata.json`).
* **Consequence:** High discriminative performance (PR-AUC = 0.7761, ROC-AUC = 0.9656, F1 = 0.8029) on unseen test transactions while maintaining an extremely low false positive rate (11 false positives out of 42,488 legitimate transactions).

---

## ADR-008: Risk Scoring Formula, Categorization Boundaries & Validation Engine
* **Status:** Accepted
* **Context:** Real-time financial transaction risk systems require an intuitive, normalized score (0–100) and standardized modeled risk categories (Low, Medium, High) for downstream operational interpretation and consumption.
* **Decision:**
  1. Map raw model fraud probability $P(\text{Class}=1) \in [0.0, 1.0]$ to integer risk score via $\text{score} = \text{round}(P \cdot 100)$ using standard mathematical half-up rounding (`Decimal.quantize(ROUND_HALF_UP)`).
  2. Classify integer risk score into non-overlapping modeled risk categories:
     - **Low:** $0 \le \text{score} \le 30$ — Lower modeled fraud risk
     - **Medium:** $31 \le \text{score} \le 70$ — Moderate modeled fraud risk
     - **High:** $71 \le \text{score} \le 100$ — Higher modeled fraud risk
  3. Enforce strict input validation in `RiskScoreEngine`: Reject non-numeric types, NaNs, infinities, and values outside $[0.0, 1.0]$ with descriptive `ValueError`/`TypeError` exceptions.
  4. Maintain constant-time ($O(1)$) execution independent of network, database, or disk I/O.
  5. Downstream transaction actions and business-policy enforcement are explicitly outside the scope of Phase 7 and will be defined during later backend development phases.
* **Consequence:** Deterministic, strictly monotonic risk assessment with clean separation between statistical risk modeling and downstream policy execution.
