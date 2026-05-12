"""
Common dependency providers for FastAPI routes.

Dependency injection in FastAPI provides:
- Clean separation of concerns
- Easy testing through mocking
- Request-scoped resource management
"""

from app.core.config import Settings, get_settings
from app.services.markdown_service import MarkdownService, get_markdown_service


async def get_settings_dep() -> Settings:
    """
    Get application settings.

    A wrapper around get_settings() for use in FastAPI dependencies.

    Returns:
        Settings: Current application settings
    """
    return get_settings()


async def get_markdown_service_dep() -> MarkdownService:
    """
    Get markdown service instance.

    A wrapper around get_markdown_service() for use in FastAPI dependencies.

    Returns:
        MarkdownService: Current markdown service instance
    """
    return get_markdown_service()


# Convenience exports for direct import
__all__ = [
    "get_settings_dep",
    "get_markdown_service_dep",
]
