"""
Pydantic schemas for aggregated transaction risk analytics.
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class RiskLabelCount(BaseModel):
    """Number of persisted evaluations assigned to one risk tier."""

    risk_label: str = Field(..., description="Risk tier category ('Low', 'Medium', 'High').", examples=["High"])
    count: int = Field(..., ge=0, description="Number of evaluations in this tier.", examples=[12])


class RiskScoreBucket(BaseModel):
    """Number of evaluations whose risk score falls within an inclusive score range."""

    score_from: int = Field(..., ge=0, le=100, description="Inclusive lower bound of the score range.", examples=[90])
    score_to: int = Field(..., ge=0, le=100, description="Inclusive upper bound of the score range.", examples=[100])
    count: int = Field(..., ge=0, description="Number of evaluations in this range.", examples=[4])


class DailyEvaluationVolume(BaseModel):
    """Evaluation counts for one UTC calendar day, split by risk tier."""

    day: date = Field(..., description="UTC calendar day.", examples=["2026-11-02"])
    low: int = Field(..., ge=0, description="Low-tier evaluations on this day.")
    medium: int = Field(..., ge=0, description="Medium-tier evaluations on this day.")
    high: int = Field(..., ge=0, description="High-tier evaluations on this day.")


class AnalyticsSummaryResponse(BaseModel):
    """Aggregate view of all persisted transaction risk evaluations."""

    total_evaluations: int = Field(..., ge=0, description="Total number of persisted evaluations.", examples=[250])
    average_risk_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Mean risk score across all evaluations; null when there are none.",
        examples=[18.4],
    )
    average_fraud_probability: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Mean fraud probability across all evaluations; null when there are none.",
        examples=[0.142],
    )
    risk_label_counts: list[RiskLabelCount] = Field(
        ...,
        description="Evaluation counts for every risk tier, ordered Low, Medium, High.",
    )
    score_distribution: list[RiskScoreBucket] = Field(
        ...,
        description="Evaluation counts in ten score ranges: 0-9, 10-19, ..., 90-100.",
    )
    daily_volume: list[DailyEvaluationVolume] = Field(
        ...,
        description="Per-day evaluation counts for the requested window, oldest first, including empty days.",
    )
    window_days: int = Field(..., ge=1, description="Number of days covered by daily_volume.", examples=[14])
