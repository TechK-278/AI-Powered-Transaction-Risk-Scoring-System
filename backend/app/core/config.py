"""
Centralized application configuration loaded from environment variables.

This module provides a singleton Settings instance that is used
throughout the application.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_env_path = Path(__file__).resolve().parent.parent.parent / ".env"


class AppSettings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    project_name: str = "AI Transaction Risk Scoring System"
    project_version: str = "1.0.0"
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 8000

    api_prefix: str = "/api/v1"
    log_level: str = "INFO"
    database_url: str = ""

    model_config = SettingsConfigDict(
        env_file=(_env_path, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

# Singleton instance of the settings
settings = AppSettings()
