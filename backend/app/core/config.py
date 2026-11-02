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

    # Comma-separated list of browser origins allowed to call the API.
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=(_env_path, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    @property
    def cors_origin_list(self) -> list[str]:
        """Return configured CORS origins as a list, ignoring blank entries."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


# Singleton instance of the settings
settings = AppSettings()
