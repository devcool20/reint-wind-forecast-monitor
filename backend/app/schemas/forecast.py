from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ForecastPoint(BaseModel):
    target_time: datetime = Field(description="The generation target time (UTC).")
    actual_generation_mw: float | None = Field(
        default=None,
        description="Actual measured wind generation in MW.",
    )
    forecast_generation_mw: float | None = Field(
        default=None,
        description="Selected forecasted wind generation in MW.",
    )
    selected_publish_time: datetime | None = Field(
        default=None,
        description="Publish time of the selected forecast (UTC).",
    )
    selected_horizon_hours: float | None = Field(
        default=None,
        description="Actual horizon of selected forecast in hours.",
    )


class ForecastMetadata(BaseModel):
    points_total: int
    points_with_actual: int
    points_with_forecast: int
    points_with_both: int


class ForecastResponse(BaseModel):
    start_time: datetime
    end_time: datetime
    forecast_horizon_hours: int
    points: list[ForecastPoint]
    metadata: ForecastMetadata

