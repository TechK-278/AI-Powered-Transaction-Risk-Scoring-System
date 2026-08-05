"""
Application entry point for the FastAPI backend.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.config import settings
from app.core.logging import logger


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for handling startup and shutdown events.
    """
    logger.info(
        "Starting %s (v%s)...",
        settings.project_name,
        settings.project_version,
    )
    yield
    logger.info(
        "Shutting down %s...",
        settings.project_name,
    )


app = FastAPI(
    title=settings.project_name,
    version=settings.project_version,
    description="Backend API for the AI-Powered Transaction Risk Scoring System.",
    debug=settings.debug,
    lifespan=lifespan,
)

# Register API routers
app.include_router(health_router, prefix=settings.api_prefix)

__all__ = ["app"]
