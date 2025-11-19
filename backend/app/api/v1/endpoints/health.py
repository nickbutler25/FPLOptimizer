"""Health check endpoint."""

from fastapi import APIRouter

from app.schemas.responses import HealthResponse
from app.core.config import settings

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the API is running and healthy",
    tags=["Health"],
)
async def health_check() -> HealthResponse:
    """Health check endpoint.

    Returns:
        HealthResponse with service status
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.environment,
    )
