"""FastAPI dependencies."""

from app.dependencies.common import (
    get_markdown_service_dep,
    get_settings_dep,
)

__all__ = [
    "get_settings_dep",
    "get_markdown_service_dep",
]
