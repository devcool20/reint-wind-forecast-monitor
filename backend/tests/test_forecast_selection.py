from __future__ import annotations

from datetime import datetime, timezone

from app.models.wind import ForecastGenerationRecord
from app.services.forecast_service import select_latest_forecast_by_horizon


def utc(year: int, month: int, day: int, hour: int, minute: int = 0) -> datetime:
    return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)


def test_selects_latest_forecast_that_meets_horizon() -> None:
    target = utc(2024, 1, 2, 12, 0)
    records = [
        ForecastGenerationRecord(start_time=target, publish_time=utc(2024, 1, 2, 7, 0), generation_mw=100.0),
        ForecastGenerationRecord(start_time=target, publish_time=utc(2024, 1, 2, 9, 0), generation_mw=105.0),
        ForecastGenerationRecord(start_time=target, publish_time=utc(2024, 1, 2, 11, 30), generation_mw=110.0),
    ]

    selected = select_latest_forecast_by_horizon(
        records,
        range_start=utc(2024, 1, 2, 0, 0),
        range_end=utc(2024, 1, 3, 0, 0),
        selected_horizon_hours=2,
        max_horizon_hours=48,
    )

    assert selected[target].publish_time == utc(2024, 1, 2, 9, 0)
    assert selected[target].generation_mw == 105.0


def test_excludes_forecasts_outside_0_48h_horizon() -> None:
    target = utc(2024, 1, 2, 12, 0)
    records = [
        ForecastGenerationRecord(start_time=target, publish_time=utc(2024, 1, 2, 12, 30), generation_mw=99.0),
        ForecastGenerationRecord(start_time=target, publish_time=utc(2023, 12, 30, 11, 0), generation_mw=95.0),
        ForecastGenerationRecord(start_time=target, publish_time=utc(2024, 1, 2, 8, 0), generation_mw=101.0),
    ]

    selected = select_latest_forecast_by_horizon(
        records,
        range_start=utc(2024, 1, 2, 0, 0),
        range_end=utc(2024, 1, 3, 0, 0),
        selected_horizon_hours=3,
        max_horizon_hours=48,
    )

    assert selected[target].publish_time == utc(2024, 1, 2, 8, 0)
    assert selected[target].generation_mw == 101.0

