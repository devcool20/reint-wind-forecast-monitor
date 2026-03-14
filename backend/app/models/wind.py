from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ActualGenerationRecord:
    start_time: datetime
    publish_time: datetime
    generation_mw: float


@dataclass(frozen=True)
class ForecastGenerationRecord:
    start_time: datetime
    publish_time: datetime
    generation_mw: float


@dataclass(frozen=True)
class SelectedForecast:
    target_time: datetime
    publish_time: datetime
    generation_mw: float
    horizon_hours: float

