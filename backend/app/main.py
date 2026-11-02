"""
Application entry point for the FastAPI backend.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.transactions import router as transactions_router
from app.core.config import settings
from app.core.logging import logger
from app.ml.loader import ModelArtifactNotFoundError, ModelLoader


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for handling startup and shutdown events.
    Pre-loads the ML inference model and preprocessor into memory.
    """
    logger.info(
        "Starting %s (v%s)...",
        settings.project_name,
        settings.project_version,
    )
    # Pre-load ML model and preprocessor artifacts during startup
    try:
        ModelLoader.load_model()
        ModelLoader.load_preprocessor()
        logger.info("ML inference artifacts successfully initialized.")
    except ModelArtifactNotFoundError:
        logger.warning(
            "ML model artifacts not found during startup. API will start, but inference endpoint will return 503 until artifacts exist."
        )
    except Exception as exc:
        logger.warning("ML initialization encountered an error: %s", exc)

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Register API routers
app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(transactions_router, prefix=settings.api_prefix)

__all__ = ["app"]

