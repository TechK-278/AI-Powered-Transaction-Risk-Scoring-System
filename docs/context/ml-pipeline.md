# Machine Learning Pipeline

## Overview
The ML subsystem is responsible for detecting transaction fraud using gradient-boosted decision trees (**XGBoost**). The subsystem spans offline research/training and online low-latency inference.

```
Offline Training Pipeline:
Raw Data ➔ Data Cleaning ➔ Feature Engineering ➔ Train/Val/Test Split ➔ XGBoost Model ➔ Evaluation ➔ Model Serialization (.joblib)

Online Inference Pipeline:
FastAPI Request ➔ Input Validation ➔ Feature Preprocessor ➔ Model Predictor ➔ Risk Score Engine ➔ Response Payload
```

---

## 1. Data Ingestion & Dataset
* **Location:** `ml/data/raw/creditcard.csv`
* **Dataset Selection:** ULB / Kaggle Credit Card Fraud Detection Dataset (284,807 European card transactions, 30 numerical input features: `Time`, `V1`..`V28` PCA components, `Amount`).
* **Target Variable:** Binary fraud indicator (`Class`: `0` = Legitimate [284,315 records, 99.827%], `1` = Fraud [492 records, 0.173%]).
* **Class Imbalance Ratio:** 577.88 : 1 (legitimate to fraudulent).
* **Missing Values:** 0 missing entries across all 31 columns.
* **Duplicates:** 1,081 duplicate transactions identified.

---

## 2. Preprocessing & Feature Engineering
* **Offline Modules:** `ml/src/preprocessing/` (`data_cleaning.py`, `feature_engineering.py`, `pipeline.py`)
* **Online Modules:** `backend/app/ml/preprocessing.py` (inherits / wraps `TransactionFeatureTransformer`)
* **Cleaning & Duplicates:** Missing values = 0; 1,081 duplicate transactions dropped (yielding 283,726 unique transactions) to prevent data leakage between train/val/test partitions.
* **Stratified Partitioning:** 70% Train (198,608 rows, 331 fraud), 15% Validation (42,559 rows, 71 fraud), 15% Test (42,559 rows, 71 fraud); Random Seed = 42; Stratified on `Class`.
* **Temporal Features:** Continuous cyclic trigonometric transformation:
  * $\text{hour} = (\text{Time} / 3600) \pmod{24}$
  * $\text{hour}_{\sin} = \sin(2\pi \cdot \text{hour} / 24)$
  * $\text{hour}_{\cos} = \cos(2\pi \cdot \text{hour} / 24)$
  * Raw elapsed `Time` is dropped to prevent temporal epoch overfitting during online inference.
* **Amount Transformation & Scaling:** $\text{amount\_log} = \log(1 + \text{Amount})$ followed by Scikit-learn `RobustScaler(with_centering=True, with_scaling=True)` fitted **strictly** on the training partition.
* **PCA Features:** Orthogonal components `V1`–`V28` passed through directly in deterministic order.
* **Preprocessed Artifact:** Serialized Scikit-learn pipeline saved to `ml/saved_models/preprocessor.joblib`.

---

## 3. Model Training & Selection
* **Algorithm:** `xgboost.XGBClassifier` (histogram tree method: `tree_method='hist'`)
* **Hyperparameter Configuration:**
  * `n_estimators`: 200
  * `max_depth`: 5
  * `learning_rate`: 0.05
  * `subsample`: 0.8
  * `colsample_bytree`: 0.8
  * `min_child_weight`: 3
  * `reg_alpha`: 0.1
  * `reg_lambda`: 1.0
  * `eval_metric`: `"logloss"`
  * `random_state`: 42
* **Handling Class Imbalance:** Dynamically calculated scale penalization: $\text{scale\_pos\_weight} = N_{\text{neg}} / N_{\text{pos}} = 198,277 / 331 = 599.02$.
* **Training Modules:** `ml/src/training/` (`train.py`, `evaluate.py`, `metrics.py`)

---

## 4. Evaluation Metrics & Threshold Optimization
* **Primary Metric:** **PR-AUC (Average Precision)** and **F1-Score** (due to 599:1 class imbalance).
* **Threshold Tuning Strategy:** Decision threshold swept across $[0.05, 0.95]$ strictly on the validation partition to maximize $F_1$-score ($\text{threshold} = 0.95$).
* **Measured Test Results (42,559 unseen test transactions):**
  * **Precision:** 83.33% (55 true fraud, 11 false alarms out of 42,488 legit)
  * **Recall:** 77.46% (55 detected out of 71 actual fraud)
  * **F1-Score:** 0.8029
  * **PR-AUC (Average Precision):** 0.7761
  * **ROC-AUC:** 0.9656
  * **Accuracy:** 99.937% (reported with context; not used as optimization objective)
  * **Confusion Matrix:** $\text{TN}=42,477, \text{FP}=11, \text{FN}=16, \text{TP}=55$

---

## 5. Model Serialization & Runtime Engine
* **Artifact Directory:** `ml/saved_models/`
* **Serialized Model:** `ml/saved_models/fraud_model.joblib`
* **Model Metadata:** `ml/saved_models/model_metadata.json`
* **Inference Loader:** `backend/app/ml/loader.py` (`TODO — Phase 8`).
* **Prediction Engine:** `backend/app/ml/predictor.py` (`TODO — Phase 8`).
* **Risk Engine:** `backend/app/ml/risk_engine.py` (`RiskScoreEngine`) converts model fraud probability $P(\text{Class}=1) \in [0.0, 1.0]$ into a deterministic integer score $\text{score} = \text{round}(P \cdot 100) \in [0, 100]$ using mathematical round-half-up, and categorizes into standard modeled risk categories:
  * **Low:** $0 \le \text{score} \le 30$ — Lower modeled fraud risk
  * **Medium:** $31 \le \text{score} \le 70$ — Moderate modeled fraud risk
  * **High:** $71 \le \text{score} \le 100$ — Higher modeled fraud risk
  * *Scope Clarification:* The Risk Score Engine defines modeled risk categories only; downstream transaction actions/policies are outside Phase 7 scope and will be determined during later backend and business-logic phases.
* **Output Structure:** `RiskAssessment(fraud_probability: float, risk_score: int, risk_label: str)`.
