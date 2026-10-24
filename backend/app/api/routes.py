from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.analysis.service import (
    build_accuracy,
    build_forecasts,
    build_insights,
    build_methodology,
    build_summary,
)
from app.config import get_settings
from app.models.schemas import (
    AccuracyResponse,
    ForecastsResponse,
    HealthResponse,
    InsightsResponse,
    MethodologyResponse,
    SummaryResponse,
)

router = APIRouter()


def _validate_delivery_date(delivery_date: Optional[date]) -> Optional[str]:
    if delivery_date is None:
        return None
    settings = get_settings()
    start = date.fromisoformat(settings.analysis_period_start)
    end = date.fromisoformat(settings.analysis_period_end)
    if delivery_date < start or delivery_date > end:
        raise HTTPException(
            status_code=400,
            detail=f"delivery_date must be between {start.isoformat()} and {end.isoformat()}",
        )
    return delivery_date.isoformat()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        application=settings.app_name,
        analysis_period_start=settings.analysis_period_start,
        analysis_period_end=settings.analysis_period_end,
    )


@router.get("/summary", response_model=SummaryResponse)
def summary(
    delivery_date: Optional[date] = Query(default=None),
    start_time: Optional[str] = Query(default=None),
) -> SummaryResponse:
    try:
        return build_summary(_validate_delivery_date(delivery_date), start_time)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/forecasts", response_model=ForecastsResponse)
def forecasts(delivery_date: Optional[date] = Query(default=None)) -> ForecastsResponse:
    try:
        payload = build_forecasts(_validate_delivery_date(delivery_date))
        if not payload.intervals:
            raise HTTPException(status_code=404, detail="No forecast intervals for the requested filter")
        return payload
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/accuracy", response_model=AccuracyResponse)
def accuracy(delivery_date: Optional[date] = Query(default=None)) -> AccuracyResponse:
    try:
        return build_accuracy(_validate_delivery_date(delivery_date))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/insights", response_model=InsightsResponse)
def insights() -> InsightsResponse:
    try:
        return build_insights()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/methodology", response_model=MethodologyResponse)
def methodology() -> MethodologyResponse:
    try:
        return build_methodology()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
