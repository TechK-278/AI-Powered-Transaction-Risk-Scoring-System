"""
API router module for transaction risk evaluation and history management endpoints.
"""

import math
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.database.session import get_db
from app.ml.loader import ModelArtifactNotFoundError, ModelLoadError
from app.ml.predictor import TransactionPredictor
from app.repositories.transaction import TransactionRepository
from app.schemas.transaction import (
    PaginatedTransactionsResponse,
    TransactionDetailResponse,
    TransactionEvaluationRequest,
    TransactionEvaluationResponse,
)

router = APIRouter(prefix="/transactions", tags=["Transactions"])

# Shared predictor instance for the API router
_predictor = TransactionPredictor()


@router.post(
    "/evaluate",
    summary="Evaluate Transaction Risk & Persist Assessment",
    description=(
        "Evaluate real-time fraud risk for a transaction payload using the trained "
        "XGBoost model, calculate risk score via Phase 7 RiskScoreEngine, and persist "
        "the resulting assessment in PostgreSQL."
    ),
    response_model=TransactionEvaluationResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Transaction successfully evaluated and persisted.",
            "model": TransactionEvaluationResponse,
        },
        400: {"description": "Invalid feature values or preprocessing error."},
        422: {"description": "Validation error for request payload schema."},
        503: {"description": "Inference service or database temporarily unavailable."},
        500: {"description": "Internal server error during risk evaluation or persistence."},
    },
)
async def evaluate_transaction(
    request: TransactionEvaluationRequest,
    db: Session = Depends(get_db),
) -> TransactionEvaluationResponse:
    """
    Evaluate real-time transaction risk scoring and persist the assessment.

    Args:
        request: Validated transaction request payload.
        db: Active SQLAlchemy database session.

    Returns:
        TransactionEvaluationResponse: Evaluated fraud probability, risk score, risk label, and record ID.
    """
    try:
        # Step 1: Execute ML inference & risk assessment
        assessment = _predictor.predict(request)

        # Step 2: Persist assessment in PostgreSQL
        record = TransactionRepository.create(
            db=db,
            amount=request.amount,
            time=request.time,
            fraud_probability=assessment.fraud_probability,
            risk_score=assessment.risk_score,
            risk_label=assessment.risk_label,
        )
        db.commit()
        db.refresh(record)

        return TransactionEvaluationResponse(
            id=record.id,
            fraud_probability=assessment.fraud_probability,
            risk_score=assessment.risk_score,
            risk_label=assessment.risk_label,
            created_at=record.created_at,
        )
    except ModelArtifactNotFoundError as exc:
        db.rollback()
        logger.error("Model artifact missing during API request: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Inference service temporarily unavailable: model artifacts not initialized.",
        ) from exc
    except ModelLoadError as exc:
        db.rollback()
        logger.error("Model artifact load error during API request: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Inference service temporarily unavailable: model loading failed.",
        ) from exc
    except ValueError as exc:
        db.rollback()
        logger.warning("Invalid transaction evaluation request: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transaction evaluation error: {exc}",
        ) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Database persistence failed during transaction evaluation: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database persistence error: failed to store transaction evaluation.",
        ) from exc
    except Exception as exc:
        db.rollback()
        logger.exception("Unexpected error during transaction evaluation: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during transaction risk evaluation.",
        ) from exc


@router.get(
    "/",
    summary="List Transaction Risk Assessments",
    description="Retrieve paginated transaction assessments with optional risk score and tier filtering.",
    response_model=PaginatedTransactionsResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Paginated transaction records matching query filters.",
            "model": PaginatedTransactionsResponse,
        },
        422: {"description": "Validation error for pagination or filter parameters."},
        500: {"description": "Database query failure."},
    },
)
async def list_transactions(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)."),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page (max 100)."),
    risk_label: Optional[str] = Query(
        default=None,
        description="Filter by risk tier category ('Low', 'Medium', 'High').",
    ),
    min_risk_score: Optional[int] = Query(
        default=None,
        ge=0,
        le=100,
        description="Filter by minimum risk score (inclusive, 0-100).",
    ),
    max_risk_score: Optional[int] = Query(
        default=None,
        ge=0,
        le=100,
        description="Filter by maximum risk score (inclusive, 0-100).",
    ),
    db: Session = Depends(get_db),
) -> PaginatedTransactionsResponse:
    """
    Retrieve paginated transaction records.

    Args:
        page: Page number (1-indexed).
        page_size: Number of items per page.
        risk_label: Optional risk tier filter.
        min_risk_score: Optional minimum risk score filter.
        max_risk_score: Optional maximum risk score filter.
        db: Active SQLAlchemy database session.

    Returns:
        PaginatedTransactionsResponse: Paginated transaction records and pagination metadata.
    """
    if min_risk_score is not None and max_risk_score is not None and min_risk_score > max_risk_score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_risk_score cannot be greater than max_risk_score.",
        )

    try:
        skip = (page - 1) * page_size
        items, total = TransactionRepository.get_paginated(
            db=db,
            skip=skip,
            limit=page_size,
            risk_label=risk_label,
            min_risk_score=min_risk_score,
            max_risk_score=max_risk_score,
        )

        total_pages = math.ceil(total / page_size) if total > 0 else 0

        return PaginatedTransactionsResponse(
            items=[TransactionDetailResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.exception("Database query failed while listing transactions: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database query error while retrieving transaction records.",
        ) from exc


@router.get(
    "/{transaction_id}",
    summary="Get Transaction Assessment by ID",
    description="Retrieve full details for a single persisted transaction evaluation record.",
    response_model=TransactionDetailResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Transaction record found.",
            "model": TransactionDetailResponse,
        },
        404: {"description": "Transaction record not found."},
        500: {"description": "Database query failure."},
    },
)
async def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
) -> TransactionDetailResponse:
    """
    Retrieve a single transaction evaluation by ID.

    Args:
        transaction_id: Unique UUID string identifier.
        db: Active SQLAlchemy database session.

    Returns:
        TransactionDetailResponse: Detailed transaction evaluation record.
    """
    try:
        transaction = TransactionRepository.get_by_id(db=db, transaction_id=transaction_id)
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction with ID '{transaction_id}' not found.",
            )
        return TransactionDetailResponse.model_validate(transaction)
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.exception("Database query failed while fetching transaction %s: %s", transaction_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while retrieving transaction record.",
        ) from exc
