from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.schemas.forecast import ForecastResponse
from app.services.forecast_service import (
    ForecastService,
    InputValidationError,
    UpstreamServiceError,
)

router = APIRouter(prefix="/api", tags=["forecasts"])


def get_forecast_service(request: Request) -> ForecastService:
    service: ForecastService | None = getattr(request.app.state, "forecast_service", None)
    if service is None:
        raise RuntimeError("Forecast service is not initialized.")
    return service


@router.get(
    "/forecasts",
    response_model=ForecastResponse,
    summary="Get actual wind generation vs selected forecast generation",
)
async def get_forecasts(
    start: datetime = Query(
        ...,
        description="UTC ISO-8601 start timestamp, inclusive (e.g. 2024-01-01T00:00:00Z)",
    ),
    end: datetime = Query(
        ...,
        description="UTC ISO-8601 end timestamp, inclusive (e.g. 2024-01-02T00:00:00Z)",
    ),
    horizon: int = Query(
        4,
        ge=0,
        le=48,
        description="Minimum forecast horizon in hours (latest forecast published at least this many hours before target time)",
    ),
    service: ForecastService = Depends(get_forecast_service),
) -> ForecastResponse:
    try:
        return await service.get_forecast_series(
            start_time=start,
            end_time=end,
            selected_horizon_hours=horizon,
        )
    except InputValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except UpstreamServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

