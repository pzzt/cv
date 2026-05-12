"""API routers."""

from app.routers.cv import router as cv_router
from app.routers.health import router as health_router
from app.routers.portfolio import router as portfolio_router

__all__ = ["cv_router", "health_router", "portfolio_router"]
