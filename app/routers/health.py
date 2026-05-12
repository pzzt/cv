"""
Health check router.

Provides liveness and readiness endpoints for container orchestration
and monitoring systems.

Why separate health router:
- Standard practice for microservices
- Required by Kubernetes/Docker health checks
- Easy to extend with dependency checks
"""

from datetime import UTC, datetime

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.cv import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])
settings = get_settings()


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns service health status, version, and environment.
    Used by container orchestrators and load balancers.

    Returns:
        HealthResponse: Current service health information
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.app_environment,
        timestamp=datetime.now(UTC),
    )
