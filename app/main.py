"""
FastAPI application entry point.

This module creates and configures the FastAPI application.
It follows a modular architecture with:
- Centralized configuration
- Structured logging
- CORS middleware
- Router aggregation
- OpenAPI documentation

Why this structure:
- Clean separation between app creation and startup
- Easy to test (can create app with test config)
- Standard FastAPI patterns for maintainability
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import Settings, get_settings
from app.routers import cv_router, health_router, portfolio_router
from app.utils.logging import LogFormat, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    FastAPI replaces on_event() with lifespan() in newer versions.

    Args:
        app: The FastAPI application instance

    Yields:
        None
    """
    # Startup
    settings: Settings = app.state.settings
    setup_logging(
        log_level=settings.log_level,
        log_format=LogFormat(settings.log_format),
    )

    import logging

    logger = logging.getLogger(__name__)
    logger.info(
        "Starting %s v%s in %s mode",
        settings.app_name,
        settings.app_version,
        settings.app_environment,
    )

    # Validate markdown file exists
    cv_file_path = settings.markdown_path
    if not cv_file_path.exists():
        logger.warning(
            "Markdown file not found at: %s. API will return 404 for CV endpoints.",
            cv_file_path,
        )
    else:
        logger.info("Markdown file loaded from: %s", cv_file_path)

    yield

    # Shutdown
    logger.info("Shutting down %s", settings.app_name)


def create_app(settings: Settings | None = None) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        settings: Application settings. Uses get_settings() if None.

    Returns:
        Configured FastAPI application instance
    """
    if settings is None:
        settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Backend API for CV/Portfolio content",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # Store settings in app state for access in lifespan
    app.state.settings = settings

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Include routers
    app.include_router(health_router, prefix="/api")
    app.include_router(cv_router, prefix="/api")
    app.include_router(portfolio_router, prefix="/api")

    # Static files for frontend
    static_dir = Path(__file__).parent.parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Root endpoint - serve the frontend HTML
    @app.get("/", include_in_schema=False, response_model=None)
    async def root() -> FileResponse | dict[str, str | None]:
        """Serve the frontend HTML."""
        html_path = Path(__file__).parent.parent / "static" / "index.html"
        if html_path.exists():
            return FileResponse(html_path)
        return {
            "message": "CV API",
            "version": settings.app_version,
            "docs": "/docs" if not settings.is_production else None,
            "health": "/api/health",
        }

    return app


# Application instance for uvicorn/direct import
app = create_app()
