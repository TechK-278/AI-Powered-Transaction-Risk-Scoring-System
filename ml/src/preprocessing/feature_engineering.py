"""
Feature engineering and transformation module.

Implements Scikit-learn compatible transformers for temporal feature extraction,
log-transformation of transaction amounts, robust scaling, and PCA feature preservation.
"""

from typing import Any, Sequence

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import RobustScaler

from ml.src.config import (
    AMOUNT_COLUMN,
    ENGINEERED_FEATURE_NAMES,
    PCA_COLUMNS,
    TIME_COLUMN,
)


class TransactionFeatureTransformer(BaseEstimator, TransformerMixin):
    """
    Scikit-learn compatible transformer for transaction risk feature engineering.

    Features engineered:
    1. Temporal Cyclicity:
       - hour_of_day = (Time / 3600.0) % 24.0
       - hour_sin = sin(2 * pi * hour_of_day / 24.0)
       - hour_cos = cos(2 * pi * hour_of_day / 24.0)
    2. Amount Transformation & Scaling:
       - amount_log = log1p(Amount)
       - amount_log_scaled = RobustScaler().fit_transform(amount_log)
    3. PCA Pass-through:
       - V1 through V28 preserved in fixed deterministic order.

    The original raw 'Time' and 'Amount' columns are dropped to eliminate collinearity
    and prevent temporal epoch overfitting during online inference.
    """

    def __init__(self, scale_amount: bool = True) -> None:
        """
        Initialize the TransactionFeatureTransformer.

        Args:
            scale_amount: Whether to apply RobustScaler to log-transformed Amount.
        """
        self.scale_amount = scale_amount
        self.amount_scaler = RobustScaler() if scale_amount else None
        self.feature_names_out_: list[str] = list(ENGINEERED_FEATURE_NAMES)
        self.is_fitted_: bool = False

    def _convert_to_dataframe(self, X: Any) -> pd.DataFrame:
        """
        Convert various input formats (dict, list of dicts, numpy array, DataFrame) to DataFrame.

        Args:
            X: Input features.

        Returns:
            pd.DataFrame: Formatted DataFrame.
        """
        if isinstance(X, pd.DataFrame):
            return X.copy()
        if isinstance(X, dict):
            return pd.DataFrame([X])
        if isinstance(X, list) and len(X) > 0 and isinstance(X[0], dict):
            return pd.DataFrame(X)
        if isinstance(X, np.ndarray):
            # Assumes columns in order: Time, V1..V28, Amount
            expected_input_cols = [TIME_COLUMN] + PCA_COLUMNS + [AMOUNT_COLUMN]
            if X.shape[1] != len(expected_input_cols):
                raise ValueError(
                    f"Array input expected {len(expected_input_cols)} features, got {X.shape[1]}"
                )
            return pd.DataFrame(X, columns=expected_input_cols)

        raise TypeError(f"Unsupported input type for feature transformation: {type(X)}")

    def _validate_input_columns(self, df: pd.DataFrame) -> None:
        """
        Validate that all required input columns exist in the DataFrame.

        Args:
            df: Input DataFrame.

        Raises:
            ValueError: If required columns are missing.
        """
        required_cols = {TIME_COLUMN, AMOUNT_COLUMN} | set(PCA_COLUMNS)
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(
                f"Input data is missing required columns: {sorted(missing)}"
            )

    def fit(self, X: Any, y: Any = None) -> "TransactionFeatureTransformer":
        """
        Fit the transformer on training feature data.

        Fits the amount scaler ONLY on training data to strictly prevent data leakage.

        Args:
            X: Training features (DataFrame, dict, or ndarray).
            y: Ignored (for sklearn pipeline compatibility).

        Returns:
            TransactionFeatureTransformer: Fitted transformer instance.
        """
        df = self._convert_to_dataframe(X)
        self._validate_input_columns(df)

        if self.scale_amount and self.amount_scaler is not None:
            # Apply log1p on training Amount
            amounts = df[AMOUNT_COLUMN].to_numpy(dtype=np.float64)
            amounts_non_negative = np.maximum(0.0, amounts)
            amount_log = np.log1p(amounts_non_negative).reshape(-1, 1)
            self.amount_scaler.fit(amount_log)

        self.is_fitted_ = True
        return self

    def transform(self, X: Any) -> np.ndarray:
        """
        Transform raw transaction features into engineered, model-ready numerical feature matrix.

        Args:
            X: Input transaction data to transform.

        Returns:
            np.ndarray: 2D array of engineered features with shape (n_samples, 31).
        """
        if not self.is_fitted_:
            raise RuntimeError(
                "TransactionFeatureTransformer must be fitted before calling transform."
            )

        df = self._convert_to_dataframe(X)
        self._validate_input_columns(df)

        # 1. Temporal cyclic feature engineering
        raw_time = df[TIME_COLUMN].to_numpy(dtype=np.float64)
        hour_of_day = (raw_time / 3600.0) % 24.0
        hour_radians = 2.0 * np.pi * (hour_of_day / 24.0)
        hour_sin = np.sin(hour_radians).reshape(-1, 1)
        hour_cos = np.cos(hour_radians).reshape(-1, 1)

        # 2. Amount log transformation & scaling
        raw_amounts = df[AMOUNT_COLUMN].to_numpy(dtype=np.float64)
        amounts_non_negative = np.maximum(0.0, raw_amounts)
        amount_log = np.log1p(amounts_non_negative).reshape(-1, 1)

        if self.scale_amount and self.amount_scaler is not None:
            amount_transformed = self.amount_scaler.transform(amount_log)
        else:
            amount_transformed = amount_log

        # 3. PCA features (V1 to V28 in deterministic order)
        pca_features = df[PCA_COLUMNS].to_numpy(dtype=np.float64)

        # 4. Concatenate: [V1..V28, hour_sin, hour_cos, amount_log_scaled]
        feature_matrix = np.hstack(
            [pca_features, hour_sin, hour_cos, amount_transformed]
        )

        return feature_matrix

    def transform_to_dataframe(self, X: Any) -> pd.DataFrame:
        """
        Transform raw features and return a labeled pandas DataFrame.

        Args:
            X: Input transaction data.

        Returns:
            pd.DataFrame: DataFrame containing engineered features with explicit column names.
        """
        matrix = self.transform(X)
        return pd.DataFrame(matrix, columns=self.get_feature_names_out())

    def get_feature_names_out(
        self, input_features: Sequence[str] | None = None
    ) -> list[str]:
        """
        Get the list of output feature names.

        Args:
            input_features: Ignored (standard sklearn interface).

        Returns:
            list[str]: Output feature column names.
        """
        return list(self.feature_names_out_)
