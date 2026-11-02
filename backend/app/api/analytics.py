"""
API router module for aggregated transaction risk analytics.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.database.session import get_db
from app.schemas.analytics import AnalyticsSummaryResponse
from app.services.analytics_service import build_analytics_summary

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/summary",
    summary="Get Transaction Risk Analytics Summary",
    description=(
        "Aggregate all persisted evaluations into totals, average score and probability, "
        "risk tier counts, a ten-range score distribution, and per-day volume by tier."
    ),
    response_model=AnalyticsSummaryResponse,
    status_code=status.HTTP_200_OK,
    responses={
        422: {"description": "Validation error for window_days."},
        500: {"description": "Database query failure."},
    },
)
def get_analytics_summary(
    window_days: int = Query(default=14, ge=1, le=90, description="Days of daily volume to return (1-90)."),
    db: Session = Depends(get_db),
) -> AnalyticsSummaryResponse:
    """
    Return the aggregated analytics summary.

    Declared as a synchronous handler so FastAPI runs the blocking database
    queries in its threadpool instead of on the event loop.
    """
    try:
        return build_analytics_summary(db=db, window_days=window_days)
    except SQLAlchemyError as exc:
        logger.exception("Database query failed while building analytics summary: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while building the analytics summary.",
        ) from exc
