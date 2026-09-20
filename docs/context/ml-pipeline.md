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
* **Algorithm:** `xgboost.XGBClassifier`
* **Hyperparameter Tuning Strategy:** `TODO — Not yet defined` (e.g., Optuna / RandomizedSearchCV).
* **Handling Class Imbalance:** `TODO — Not yet defined` (e.g. `scale_pos_weight`, SMOTE, PR-AUC thresholding).

---

## 4. Evaluation Metrics
* **Key Metrics:** Precision, Recall, F1-score, ROC-AUC, PR-AUC (Precision-Recall AUC), Confusion Matrix.
* **Evaluation Scripts:** `ml/evaluation/` (`TODO — Not yet defined`).

---

## 5. Model Serialization & Runtime Engine
* **Artifact Directory:** `ml/saved_models/`
* **Serialization Format:** `.joblib` / `.json`
* **Inference Loader:** `backend/app/ml/loader.py` (`TODO — Not yet defined`).
* **Prediction Engine:** `backend/app/ml/predictor.py` (`TODO — Not yet defined`).
* **Risk Engine:** `backend/app/ml/risk_engine.py` converts fraud probabilities to 0–100 integer scores with threshold categorization.
