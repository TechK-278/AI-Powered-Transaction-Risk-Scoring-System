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
* **Offline Modules:** `ml/preprocessing/`, `ml/features/`
* **Online Modules:** `backend/app/ml/preprocessing.py`
* **Handling Missing Values:** `TODO — Not yet defined`
* **Encoding Categorical Features:** `TODO — Not yet defined` (e.g., Target Encoding / One-Hot / Frequency Encoding).
* **Numerical Scaling:** `TODO — Not yet defined`
* **Temporal & Behavioral Features:** `TODO — Not yet defined` (e.g. transaction hour, transaction frequency, amount vs user average).

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
