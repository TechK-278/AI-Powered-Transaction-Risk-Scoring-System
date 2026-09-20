"""
Central configuration for ML preprocessing and training pipelines.

Defines reproducible constants, directory paths, feature schemas,
and split ratios for the AI-Powered Transaction Risk Scoring System.
"""

from pathlib import Path

# Base Paths (Resolve relative to repository root)
SRC_DIR = Path(__file__).resolve().parent
ML_DIR = SRC_DIR.parent
PROJECT_ROOT = ML_DIR.parent

# Data Paths
RAW_DATA_DIR = ML_DIR / "data" / "raw"
PROCESSED_DATA_DIR = ML_DIR / "data" / "processed"
SAVED_MODELS_DIR = ML_DIR / "saved_models"

RAW_DATA_FILE = RAW_DATA_DIR / "creditcard.csv"
TRAIN_DATA_FILE = PROCESSED_DATA_DIR / "train.csv"
VAL_DATA_FILE = PROCESSED_DATA_DIR / "validation.csv"
TEST_DATA_FILE = PROCESSED_DATA_DIR / "test.csv"

# Preprocessor Artifact Path
PREPROCESSOR_ARTIFACT_FILE = SAVED_MODELS_DIR / "preprocessor.joblib"

# Reproducibility Seed
RANDOM_SEED = 42

# Dataset Schema Definitions
TARGET_COLUMN = "Class"
TIME_COLUMN = "Time"
AMOUNT_COLUMN = "Amount"
PCA_COLUMNS = [f"V{i}" for i in range(1, 29)]

EXPECTED_COLUMNS = [TIME_COLUMN] + PCA_COLUMNS + [AMOUNT_COLUMN, TARGET_COLUMN]
FEATURE_COLUMNS = [TIME_COLUMN] + PCA_COLUMNS + [AMOUNT_COLUMN]

# Dataset Split Ratios
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

# Engineered Feature Names (Output order from preprocessor)
ENGINEERED_FEATURE_NAMES = (
    PCA_COLUMNS
    + ["hour_sin", "hour_cos", "amount_log"]
)
