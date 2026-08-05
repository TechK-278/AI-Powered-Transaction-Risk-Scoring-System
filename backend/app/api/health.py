"""
API health check endpoint module.
"""

from app.schemas.health import HealthResponse
from typing import Dict

from fastapi import APIRouter

from app.core.config import settings


router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "/",
    summary="Health Check",
    response_model=HealthResponse,
)
async def health_check() -> HealthResponse:
    """
    Endpoint to verify the service is running and responsive.

    Returns basic application information including the status,
    service name, and current version.
    """
    return HealthResponse(
        status="healthy",
        service=settings.project_name,
        version=settings.project_version,
    )
