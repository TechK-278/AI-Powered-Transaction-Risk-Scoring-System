"""
Data cleaning and dataset splitting module.

Provides validated loading, anomaly checks, duplicate management,
and stratified train/validation/test splitting for tabular transaction data.
"""

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from ml.src.config import (
    EXPECTED_COLUMNS,
    RANDOM_SEED,
    TARGET_COLUMN,
    TEST_RATIO,
    TRAIN_RATIO,
    VAL_RATIO,
)


def load_raw_data(file_path: Path | str) -> pd.DataFrame:
    """
    Load raw transaction data from CSV file.

    Args:
        file_path: Path to the raw CSV file.

    Returns:
        pd.DataFrame: Loaded dataset.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If the file is empty.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Raw data file not found at: {path}")

    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"Raw data file at {path} is empty.")

    return df


def validate_raw_data(df: pd.DataFrame) -> None:
    """
    Validate that the DataFrame contains expected columns and valid target values.

    Args:
        df: Input DataFrame to validate.

    Raises:
        ValueError: If required columns are missing or target values are invalid.
    """
    if df.empty:
        raise ValueError("Cannot validate an empty DataFrame.")

    missing_cols = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing expected columns in dataset: {sorted(missing_cols)}")

    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Target column '{TARGET_COLUMN}' not found in dataset.")

    unique_targets = set(df[TARGET_COLUMN].dropna().unique())
    if not unique_targets.issubset({0, 1}):
        raise ValueError(
            f"Target column '{TARGET_COLUMN}' must contain only binary values (0, 1). Found: {unique_targets}"
        )


def clean_dataset(
    df: pd.DataFrame, drop_duplicates_flag: bool = True
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Clean the raw dataset, checking for missing values, infinite values, and duplicates.

    Args:
        df: Raw DataFrame.
        drop_duplicates_flag: Whether to drop duplicate rows. Defaults to True.

    Returns:
        tuple[pd.DataFrame, dict[str, Any]]: Cleaned DataFrame and cleaning summary metrics.
    """
    validate_raw_data(df)
    initial_rows = len(df)
    cleaning_metrics: dict[str, Any] = {
        "initial_rows": initial_rows,
        "initial_cols": df.shape[1],
    }

    # 1. Missing value check
    null_counts = df.isnull().sum()
    total_nulls = int(null_counts.sum())
    cleaning_metrics["total_null_values"] = total_nulls
    cleaning_metrics["columns_with_nulls"] = null_counts[null_counts > 0].to_dict()

    cleaned_df = df.copy()
    if total_nulls > 0:
        cleaned_df = cleaned_df.dropna()

    # 2. Infinite value check
    numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
    inf_counts = np.isinf(cleaned_df[numeric_cols]).sum()
    total_infs = int(inf_counts.sum())
    cleaning_metrics["total_inf_values"] = total_infs

    if total_infs > 0:
        cleaned_df = cleaned_df.replace([np.inf, -np.inf], np.nan).dropna()

    # 3. Duplicate handling
    duplicate_mask = cleaned_df.duplicated()
    total_duplicates = int(duplicate_mask.sum())
    duplicates_by_class = cleaned_df.loc[duplicate_mask, TARGET_COLUMN].value_counts().to_dict()

    cleaning_metrics["total_duplicates"] = total_duplicates
    cleaning_metrics["duplicates_by_class"] = duplicates_by_class
    cleaning_metrics["drop_duplicates_applied"] = drop_duplicates_flag

    if drop_duplicates_flag and total_duplicates > 0:
        cleaned_df = cleaned_df.drop_duplicates(keep="first").reset_index(drop=True)

    cleaning_metrics["final_rows"] = len(cleaned_df)
    cleaning_metrics["removed_rows"] = initial_rows - len(cleaned_df)

    return cleaned_df, cleaning_metrics


def split_dataset(
    df: pd.DataFrame,
    target_col: str = TARGET_COLUMN,
    train_ratio: float = TRAIN_RATIO,
    val_ratio: float = VAL_RATIO,
    test_ratio: float = TEST_RATIO,
    random_seed: int = RANDOM_SEED,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    """
    Split a DataFrame into stratified train, validation, and test subsets.

    Args:
        df: Cleaned DataFrame.
        target_col: Target column name for stratification.
        train_ratio: Proportion for training set (e.g., 0.70).
        val_ratio: Proportion for validation set (e.g., 0.15).
        test_ratio: Proportion for test set (e.g., 0.15).
        random_seed: Random seed for deterministic reproducibility.

    Returns:
        tuple containing (X_train, X_val, X_test, y_train, y_val, y_test).

    Raises:
        ValueError: If split ratios do not sum to 1.0 within tolerance.
    """
    if not np.isclose(train_ratio + val_ratio + test_ratio, 1.0):
        raise ValueError(
            f"Split ratios must sum to 1.0. Found: {train_ratio} + {val_ratio} + {test_ratio} = {train_ratio + val_ratio + test_ratio}"
        )

    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in DataFrame.")

    feature_cols = [c for c in df.columns if c != target_col]
    X = df[feature_cols]
    y = df[target_col]

    # Step 1: Split into Train and Temp (Val + Test)
    temp_ratio = val_ratio + test_ratio
    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=temp_ratio,
        random_state=random_seed,
        stratify=y,
    )

    # Step 2: Split Temp into Validation and Test
    val_relative_ratio = val_ratio / temp_ratio
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=(1.0 - val_relative_ratio),
        random_state=random_seed,
        stratify=y_temp,
    )

    return (
        X_train.reset_index(drop=True),
        X_val.reset_index(drop=True),
        X_test.reset_index(drop=True),
        y_train.reset_index(drop=True),
        y_val.reset_index(drop=True),
        y_test.reset_index(drop=True),
    )
