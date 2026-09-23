"""
API router module for transaction risk evaluation endpoints.
"""

from fastapi import APIRouter, HTTPException, status

from app.core.logging import logger
from app.ml.loader import ModelArtifactNotFoundError, ModelLoadError
from app.ml.predictor import TransactionPredictor
from app.schemas.transaction import (
    TransactionEvaluationRequest,
    TransactionEvaluationResponse,
)

router = APIRouter(prefix="/transactions", tags=["Transactions"])

# Shared predictor instance for the API router
_predictor = TransactionPredictor()


@router.post(
    "/evaluate",
    summary="Evaluate Transaction Risk",
    description=(
        "Evaluate real-time fraud risk for a single transaction payload using the "
        "trained XGBoost model and Phase 7 RiskScoreEngine."
    ),
    response_model=TransactionEvaluationResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Transaction successfully evaluated.",
            "model": TransactionEvaluationResponse,
        },
        400: {"description": "Invalid feature values or preprocessing error."},
        422: {"description": "Validation error for request payload schema."},
        503: {"description": "Inference service unavailable (model artifact missing or loading error)."},
        500: {"description": "Internal server error during risk evaluation."},
    },
)
async def evaluate_transaction(
    request: TransactionEvaluationRequest,
) -> TransactionEvaluationResponse:
    """
    Evaluate real-time transaction risk scoring.

    Args:
        request: Validated transaction request payload.

    Returns:
        TransactionEvaluationResponse: Evaluated fraud probability, risk score, and risk label.
    """
    try:
        assessment = _predictor.predict(request)
        return TransactionEvaluationResponse(
            fraud_probability=assessment.fraud_probability,
            risk_score=assessment.risk_score,
            risk_label=assessment.risk_label,
        )
    except ModelArtifactNotFoundError as exc:
        logger.error("Model artifact missing during API request: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Inference service temporarily unavailable: model artifacts not initialized.",
        ) from exc
    except ModelLoadError as exc:
        logger.error("Model artifact load error during API request: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Inference service temporarily unavailable: model loading failed.",
        ) from exc
    except ValueError as exc:
        logger.warning("Invalid transaction evaluation request: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transaction evaluation error: {exc}",
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error during transaction evaluation: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during transaction risk evaluation.",
        ) from exc
