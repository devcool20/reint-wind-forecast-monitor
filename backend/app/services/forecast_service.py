from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any

from app.core.config import Settings
from app.core.datetime_utils import ensure_utc, parse_utc
from app.models.wind import (
    ActualGenerationRecord,
    ForecastGenerationRecord,
    SelectedForecast,
)
from app.schemas.forecast import ForecastMetadata, ForecastPoint, ForecastResponse
from app.services.bmrs_client import BMRSClient, BMRSClientError


class InputValidationError(ValueError):
    """Raised when API input values are invalid for business constraints."""


class UpstreamServiceError(RuntimeError):
    """Raised when upstream BMRS data cannot be retrieved reliably."""


def select_latest_forecast_by_horizon(
    forecast_records: list[ForecastGenerationRecord],
    *,
    range_start: datetime,
    range_end: datetime,
    selected_horizon_hours: int,
    max_horizon_hours: int,
) -> dict[datetime, SelectedForecast]:
    threshold_delta = timedelta(hours=selected_horizon_hours)
    selected: dict[datetime, SelectedForecast] = {}

    for record in forecast_records:
        if record.start_time < range_start or record.start_time > range_end:
            continue

        horizon_hours = (record.start_time - record.publish_time).total_seconds() / 3600
        if horizon_hours < 0 or horizon_hours > max_horizon_hours:
            continue

        if record.publish_time > (record.start_time - threshold_delta):
            continue

        existing = selected.get(record.start_time)
        if existing is None or record.publish_time > existing.publish_time:
            selected[record.start_time] = SelectedForecast(
                target_time=record.start_time,
                publish_time=record.publish_time,
                generation_mw=record.generation_mw,
                horizon_hours=horizon_hours,
            )

    return selected


class ForecastService:
    def __init__(self, settings: Settings, bmrs_client: BMRSClient) -> None:
        self._settings = settings
        self._bmrs_client = bmrs_client
        self._january_start = parse_utc(settings.january_start_utc)
        self._january_end = parse_utc(settings.january_end_utc)

    async def get_forecast_series(
        self,
        *,
        start_time: datetime,
        end_time: datetime,
        selected_horizon_hours: int,
    ) -> ForecastResponse:
        start_time = ensure_utc(start_time)
        end_time = ensure_utc(end_time)

        self._validate_inputs(
            start_time=start_time,
            end_time=end_time,
            selected_horizon_hours=selected_horizon_hours,
        )

        actual_publish_from = max(self._january_start, start_time)
        actual_publish_to = min(self._january_end + timedelta(hours=1), end_time + timedelta(hours=1))

        forecast_publish_from = max(
            self._january_start - timedelta(hours=self._settings.max_horizon_hours),
            start_time - timedelta(hours=self._settings.max_horizon_hours),
        )
        forecast_publish_to = min(self._january_end, end_time)

        try:
            actual_raw, forecast_raw = await asyncio.gather(
                self._bmrs_client.fetch_actual_generation(
                    publish_from=actual_publish_from,
                    publish_to=actual_publish_to,
                ),
                self._bmrs_client.fetch_forecast_generation(
                    publish_from=forecast_publish_from,
                    publish_to=forecast_publish_to,
                ),
            )
        except BMRSClientError as exc:
            raise UpstreamServiceError("Failed to fetch BMRS data.") from exc

        actual_records = self._parse_actual_records(actual_raw)
        forecast_records = self._parse_forecast_records(forecast_raw)

        actual_by_target = self._select_latest_actuals(
            actual_records,
            range_start=start_time,
            range_end=end_time,
        )
        forecast_by_target = select_latest_forecast_by_horizon(
            forecast_records,
            range_start=start_time,
            range_end=end_time,
            selected_horizon_hours=selected_horizon_hours,
            max_horizon_hours=self._settings.max_horizon_hours,
        )

        target_times = sorted(set(actual_by_target.keys()) | set(forecast_by_target.keys()))
        points: list[ForecastPoint] = []

        for target_time in target_times:
            actual = actual_by_target.get(target_time)
            forecast = forecast_by_target.get(target_time)
            points.append(
                ForecastPoint(
                    target_time=target_time,
                    actual_generation_mw=actual.generation_mw if actual else None,
                    forecast_generation_mw=forecast.generation_mw if forecast else None,
                    selected_publish_time=forecast.publish_time if forecast else None,
                    selected_horizon_hours=round(forecast.horizon_hours, 3) if forecast else None,
                )
            )

        metadata = ForecastMetadata(
            points_total=len(points),
            points_with_actual=sum(1 for point in points if point.actual_generation_mw is not None),
            points_with_forecast=sum(1 for point in points if point.forecast_generation_mw is not None),
            points_with_both=sum(
                1
                for point in points
                if point.actual_generation_mw is not None and point.forecast_generation_mw is not None
            ),
        )

        return ForecastResponse(
            start_time=start_time,
            end_time=end_time,
            forecast_horizon_hours=selected_horizon_hours,
            points=points,
            metadata=metadata,
        )

    def _validate_inputs(
        self,
        *,
        start_time: datetime,
        end_time: datetime,
        selected_horizon_hours: int,
    ) -> None:
        if start_time >= end_time:
            raise InputValidationError("start must be earlier than end.")

        if selected_horizon_hours < self._settings.min_horizon_hours:
            raise InputValidationError(
                f"horizon must be >= {self._settings.min_horizon_hours} hours."
            )
        if selected_horizon_hours > self._settings.max_horizon_hours:
            raise InputValidationError(
                f"horizon must be <= {self._settings.max_horizon_hours} hours."
            )

        if start_time < self._january_start or end_time > self._january_end:
            raise InputValidationError(
                "Date range must be within January 2024 UTC (2024-01-01T00:00:00Z to 2024-02-01T00:00:00Z)."
            )

    def _parse_actual_records(
        self,
        rows: list[dict[str, Any]],
    ) -> list[ActualGenerationRecord]:
        records: list[ActualGenerationRecord] = []
        for row in rows:
            if row.get("fuelType") != "WIND":
                continue
            try:
                start_time = parse_utc(str(row["startTime"]))
                publish_time = parse_utc(str(row["publishTime"]))
                generation_mw = float(row["generation"])
            except (KeyError, TypeError, ValueError):
                continue
            records.append(
                ActualGenerationRecord(
                    start_time=start_time,
                    publish_time=publish_time,
                    generation_mw=generation_mw,
                )
            )
        return records

    def _parse_forecast_records(
        self,
        rows: list[dict[str, Any]],
    ) -> list[ForecastGenerationRecord]:
        records: list[ForecastGenerationRecord] = []
        for row in rows:
            try:
                start_time = parse_utc(str(row["startTime"]))
                publish_time = parse_utc(str(row["publishTime"]))
                generation_mw = float(row["generation"])
            except (KeyError, TypeError, ValueError):
                continue
            records.append(
                ForecastGenerationRecord(
                    start_time=start_time,
                    publish_time=publish_time,
                    generation_mw=generation_mw,
                )
            )
        return records

    def _select_latest_actuals(
        self,
        records: list[ActualGenerationRecord],
        *,
        range_start: datetime,
        range_end: datetime,
    ) -> dict[datetime, ActualGenerationRecord]:
        selected: dict[datetime, ActualGenerationRecord] = {}

        for record in records:
            if record.start_time < range_start or record.start_time > range_end:
                continue
            existing = selected.get(record.start_time)
            if existing is None or record.publish_time > existing.publish_time:
                selected[record.start_time] = record

        return selected

