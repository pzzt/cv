"""
Configuration layer for the application.

Uses pydantic-settings for type-safe environment variable parsing with validation.
All configuration is centralized here and loaded once at application startup.

Why this approach:
- Type safety: Pydantic validates types at startup
- Documentation: Self-documenting through field types and defaults
- Testability: Easy to override in tests
- Immutability: Frozen settings prevent accidental runtime changes
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration.

    Settings are loaded from environment variables with fallback to .env file.
    All fields have sensible defaults for local development.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="CV_API_",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "CV API"
    app_version: str = "1.0.0"
    app_environment: str = Field(
        default="development",
        description="Application environment (development, staging, production)",
    )

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins for frontend access",
    )

    # Content
    markdown_path: Path = Field(
        default=Path("data/mycv.md"),
        description="Path to the markdown CV file",
    )

    # Features
    enable_hot_reload: bool = Field(
        default=False,
        description="Enable automatic markdown file reload on changes",
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    log_format: str = Field(
        default="json",
        description="Log format: json or plain",
    )

    @field_validator("markdown_path")
    @classmethod
    def validate_markdown_path(cls, v: Path | str) -> Path:
        """Ensure markdown_path is a Path object."""
        return Path(v) if isinstance(v, str) else v

    @field_validator("app_environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is one of the expected values."""
        valid_envs = {"development", "staging", "production", "testing"}
        if v not in valid_envs:
            raise ValueError(f"app_environment must be one of {valid_envs}")
        return v

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, v: list[str] | str) -> list[str]:
        """Support both string (comma-separated) and list for CORS origins."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_environment == "development"


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings getter.

    Why cache:
    - Settings are loaded once and reused
    - Environment variables don't change during runtime
    - Avoids repeated file I/O for .env parsing

    Returns:
        Settings: Validated application settings
    """
    return Settings()
