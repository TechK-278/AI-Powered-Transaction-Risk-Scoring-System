# Exploratory Data Analysis & Data Quality Report

**Project:** AI-Powered Transaction Risk Scoring System  
**Phase:** Phase 04 — Dataset Selection & Exploratory Data Analysis (EDA)  
**Notebook Reference:** [ml/notebooks/01_dataset_eda.ipynb](file:///e:/Project/AI%20Transaction%20Risk%20System/ml/notebooks/01_dataset_eda.ipynb)  
**Dataset Artifact:** `ml/data/raw/creditcard.csv`  

---

## 1. Executive Summary

This report documents the findings from the exploratory data analysis conducted on the **European Credit Card Fraud Detection Dataset** (Kaggle / Machine Learning Group, Université Libre de Bruxelles). The primary objective is to evaluate data quality, characterize distribution anomalies, profile class imbalance, and outline concrete preprocessing requirements for **Phase 05 (Data Preprocessing & Feature Engineering)**.

---

## 2. Dataset Provenance & Overview

| Attribute | Specification |
| :--- | :--- |
| **Dataset Name** | Credit Card Fraud Detection (European Cardholders) |
| **Original Creators** | Machine Learning Group (MLG) — Université Libre de Bruxelles (ULB) & Worldline |
| **Licensing** | Database Contents License (DbCL) / Open Database License (ODbL) v1.0 |
| **Source URL** | [Kaggle: Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) |
| **File Format / Size** | CSV / 150.83 MB (150,828,752 bytes) |
| **Observation Count** | **284,807 transactions** |
| **Total Features** | **31 columns** (30 input features + 1 binary target) |
| **Temporal Span** | 172,792 seconds (~48.0 hours / 2 consecutive days in September 2013) |

---

## 3. Feature Anatomy & Schema Definition

The dataset comprises 31 numerical columns:

```
[Time] (Seconds elapsed from first transaction)
   ├── Continuous, range [0, 172792]
   └── Exhibits strong 24-hour cyclical periodicity

[V1 - V28] (Anonymized PCA Components)
   ├── Continuous numerical features
   ├── Orthogonal principal components (zero linear collinearity)
   └── Centered near 0 with varying variance and kurtosis

[Amount] (Transaction amount in Euros)
   ├── Continuous monetary value, range [0.00, 25691.16]
   ├── Heavily right-skewed (Mean: €88.35, Median: €22.00)
   └── Requires log-transformation and robust scaling

[Class] (Supervised Binary Target)
   ├── 0 = Legitimate transaction (99.827%)
   └── 1 = Fraudulent transaction (0.173%)
```

---

## 4. Class Imbalance Analysis

Financial fraud is inherently a high-consequence, extreme anomaly detection problem:

| Class | Label | Transaction Count | Percentage | Imbalance Ratio |
| :---: | :--- | :---: | :---: | :---: |
| **0** | **Legitimate** | 284,315 | **99.8273%** | — |
| **1** | **Fraudulent** | 492 | **0.1727%** | **577.88 : 1** |
| **Total** | — | 284,807 | 100.0000% | — |

### Key Implications for Machine Learning:
1. **Accuracy is a Deceptive Metric:** A naive dummy model predicting `Class = 0` for every transaction achieves an **accuracy of 99.83%** while catching **0% of fraud**.
2. **Primary Evaluation Metrics:** Models must be optimized and evaluated on:
   * **PR-AUC (Precision-Recall Area Under Curve / Average Precision)** — Primary metric for severe imbalance.
   * **ROC-AUC (Receiver Operating Characteristic AUC)**.
   * **Recall at High Precision Thresholds** (minimizing false negatives).
3. **Loss Function Calibration:** Gradient boosting algorithms like XGBoost must be configured with `scale_pos_weight = 577.88` to penalize misclassified fraud instances proportionally.

---

## 5. Data Quality & Integrity Assessment

### 5.1 Missing Values
* **Result:** **0 missing / null values** across all 284,807 rows and 31 columns.
* **Assessment:** Clean tabular integrity; no imputation algorithms are required.

### 5.2 Duplicate Records
* **Result:** **1,081 duplicate rows** detected (0.38% of total dataset).
  * **Class 0 Duplicates:** 1,062 rows.
  * **Class 1 Duplicates:** 19 rows.
* **Assessment:** Because transactions are anonymized without cardholder IDs or merchant names, identical transactions in quick succession can represent legitimate automated micro-charges or repeated automated replay attacks.
* **Phase 5 Strategy:** Deduplication should be evaluated strictly on the training partition to prevent identical row leakage between train and validation splits.

### 5.3 Monetary Distribution (`Amount`)
* **Legitimate Transactions:** Mean = €88.29, Median = €22.00, Min = €0.00, Max = €25,691.16, IQR = €76.05.
* **Fraudulent Transactions:** Mean = €122.21, Median = €9.25, Min = €0.00, Max = €2,125.87, IQR = €104.85.
* **Finding:** Fraudulent transactions exhibit a higher mean amount (€122.21 vs €88.29) but do not reach the extreme high-dollar values (€25,691) seen in legitimate corporate/wire transactions. Over 75% of fraud transactions are under €105.89.

---

## 6. Feature Correlation & Discriminative Signals

Pearson correlation analysis with the target `Class` reveals clear, highly discriminative features:

### Top Negative Correlations (Higher feature value $\rightarrow$ Lower fraud probability):
1. **`V17`:** $r = -0.3265$ (Strongest single negative separator)
2. **`V14`:** $r = -0.3025$
3. **`V12`:** $r = -0.2606$
4. **`V10`:** $r = -0.2169$
5. **`V16`:** $r = -0.1965$

### Top Positive Correlations (Higher feature value $\rightarrow$ Higher fraud probability):
1. **`V11`:** $r = +0.1549$ (Strongest positive separator)
2. **`V4`:**  $r = +0.1334$
3. **`V2`:**  $r = +0.0913$
4. **`V21`:** $r = +0.0404$
5. **`V19`:** $r = +0.0348$

---

## 7. Data Leakage & Risk Analysis

| Leakage Risk | Mechanism | Prevention Rule for Phase 5 |
| :--- | :--- | :--- |
| **Scaler / Transformation Leakage** | Fitting scalers on full dataset prior to splitting | Fit all scalers (`RobustScaler`, `StandardScaler`) **strictly on training folds** inside `sklearn.pipeline.Pipeline`. |
| **Temporal Leakage** | Random shuffling across time boundaries | Ensure temporal ordering or **Stratified K-Fold Cross-Validation** with leakage-free pipeline encapsulation. |
| **Duplicate Leakage** | Duplicated rows appearing in both train and validation | Remove duplicates before cross-validation splitting or verify group independence. |

---

## 8. Actionable Preprocessing & Feature Engineering Plan (Phase 5)

Based on the verified findings of this EDA, Phase 5 will implement the following:

1. **Feature Engineering:**
   * `Hour_of_Day` = `(Time % 86400) / 3600` (Captures diurnal circadian patterns).
   * `Log_Amount` = $\log(1 + \text{Amount})$ (Normalizes extreme right-skew).
   * Interaction features between top discriminators (`V17 * V14`, `V12 * V10`).
2. **Feature Scaling:**
   * Apply `sklearn.preprocessing.RobustScaler` to `Amount` and `Time` to remain resilient against extreme outliers.
   * `V1`–`V28` are already zero-centered PCA components and do not require additional variance scaling.
3. **Cross-Validation Architecture:**
   * 5-fold **Stratified K-Fold** cross-validation to guarantee consistent 0.173% fraud representation across all evaluation folds.
4. **Offline ML Pipeline Modularity:**
   * Encapsulate all transformations in reusable Scikit-learn transformers under `ml/preprocessing/` and `ml/features/`.
   * Ensure identical transformer serialization for low-latency online inference in `backend/app/ml/`.
