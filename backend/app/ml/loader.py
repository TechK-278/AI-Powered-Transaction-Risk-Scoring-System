"""
Model and preprocessor artifact loader module.

Provides singleton caching, thread-safe access, and robust error handling
for loading serialized ML artifacts without per-request disk overhead.
"""

import sys
from pathlib import Path
from typing import Any, Optional
import joblib

from app.core.logging import logger


class ModelArtifactNotFoundError(RuntimeError):
    """Raised when a required ML model or preprocessor artifact cannot be located on disk."""
    pass


class ModelLoadError(RuntimeError):
    """Raised when an ML artifact fails to load or is corrupted."""
    pass


class ModelLoader:
    """
    Singleton artifact manager for ML models and preprocessors.

    Caches loaded artifacts in memory to prevent repeated disk I/O during online inference.
    """

    _model: Optional[Any] = None
    _preprocessor: Optional[Any] = None
    _model_path: Optional[Path] = None
    _preprocessor_path: Optional[Path] = None

    @classmethod
    def _project_root(cls) -> Path:
        """Resolve the project root directory."""
        current_dir = Path(__file__).resolve().parent
        # backend/app/ml/loader.py -> backend/app/ml -> backend/app -> backend -> project_root
        return current_dir.parent.parent.parent

    @classmethod
    def _default_artifact_dir(cls) -> Path:
        """Resolve the default directory containing saved ML artifacts."""
        return cls._project_root() / "ml" / "saved_models"

    @classmethod
    def _ensure_project_in_sys_path(cls) -> None:
        """Ensure project root is in sys.path so unpickling ML pipeline components succeeds."""
        project_root_str = str(cls._project_root())
        if project_root_str not in sys.path:
            sys.path.insert(0, project_root_str)

    @classmethod
    def load_model(cls, model_path: Optional[Path | str] = None) -> Any:
        """
        Load and cache the trained XGBoost fraud classification model.

        Args:
            model_path: Optional explicit path to fraud_model.joblib.

        Returns:
            Any: Loaded model instance.

        Raises:
            ModelArtifactNotFoundError: If artifact file does not exist.
            ModelLoadError: If artifact is corrupted or fails deserialization.
        """
        if cls._model is not None and model_path is None:
            return cls._model

        path = Path(model_path) if model_path else cls._default_artifact_dir() / "fraud_model.joblib"
        cls._model_path = path

        if not path.is_file():
            logger.error("Model artifact not found at expected path: %s", path)
            raise ModelArtifactNotFoundError(
                "Trained fraud detection model artifact not found. Please run offline training pipeline first."
            )

        try:
            cls._ensure_project_in_sys_path()
            logger.info("Loading fraud detection model artifact from disk...")
            cls._model = joblib.load(path)
            logger.info("Fraud detection model successfully loaded and cached in memory.")
            return cls._model
        except Exception as exc:
            logger.exception("Failed to load model artifact from path %s: %s", path, exc)
            raise ModelLoadError("Failed to deserialize model artifact.") from exc

    @classmethod
    def load_preprocessor(cls, preprocessor_path: Optional[Path | str] = None) -> Any:
        """
        Load and cache the feature engineering preprocessor pipeline.

        Args:
            preprocessor_path: Optional explicit path to preprocessor.joblib.

        Returns:
            Any: Loaded preprocessor pipeline instance.

        Raises:
            ModelArtifactNotFoundError: If artifact file does not exist.
            ModelLoadError: If artifact is corrupted or fails deserialization.
        """
        if cls._preprocessor is not None and preprocessor_path is None:
            return cls._preprocessor

        path = Path(preprocessor_path) if preprocessor_path else cls._default_artifact_dir() / "preprocessor.joblib"
        cls._preprocessor_path = path

        if not path.is_file():
            logger.error("Preprocessor artifact not found at expected path: %s", path)
            raise ModelArtifactNotFoundError(
                "Preprocessor artifact not found. Please run offline preprocessing pipeline first."
            )

        try:
            cls._ensure_project_in_sys_path()
            logger.info("Loading preprocessor artifact from disk...")
            cls._preprocessor = joblib.load(path)
            logger.info("Preprocessor artifact successfully loaded and cached in memory.")
            return cls._preprocessor
        except Exception as exc:
            logger.exception("Failed to load preprocessor artifact from path %s: %s", path, exc)
            raise ModelLoadError("Failed to deserialize preprocessor artifact.") from exc

    @classmethod
    def get_model(cls) -> Any:
        """
        Retrieve cached model instance, loading from default path if not yet initialized.

        Returns:
            Any: Loaded model instance.
        """
        if cls._model is None:
            return cls.load_model()
        return cls._model

    @classmethod
    def get_preprocessor(cls) -> Any:
        """
        Retrieve cached preprocessor instance, loading from default path if not yet initialized.

        Returns:
            Any: Loaded preprocessor instance.
        """
        if cls._preprocessor is None:
            return cls.load_preprocessor()
        return cls._preprocessor

    @classmethod
    def is_loaded(cls) -> bool:
        """Check if both model and preprocessor are loaded in memory."""
        return cls._model is not None and cls._preprocessor is not None

    @classmethod
    def reset(cls) -> None:
        """Reset cached artifact instances (useful for testing)."""
        cls._model = None
        cls._preprocessor = None
        cls._model_path = None
        cls._preprocessor_path = None
