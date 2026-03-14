from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "REint Wind Forecast API"
    app_env: str = "development"
    log_level: str = "INFO"

    bmrs_base_url: str = "https://data.elexon.co.uk/bmrs/api/v1"
    bmrs_timeout_seconds: float = 20.0
    bmrs_max_retries: int = 3
    bmrs_backoff_seconds: float = 0.5

    # Accept either a CSV string (".env") or a JSON/list value.
    cors_allow_origins: str | list[str] = "http://localhost:3000"

    min_horizon_hours: int = 0
    max_horizon_hours: int = 48
    default_horizon_hours: int = 4

    january_start_utc: str = "2024-01-01T00:00:00Z"
    january_end_utc: str = "2024-02-01T00:00:00Z"

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def parse_cors_allow_origins(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        raise ValueError("cors_allow_origins must be a CSV string or a list.")

    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        return value.upper().strip()

    @model_validator(mode="after")
    def validate_horizon_bounds(self) -> "Settings":
        if self.min_horizon_hours < 0:
            raise ValueError("min_horizon_hours must be >= 0.")
        if self.max_horizon_hours <= self.min_horizon_hours:
            raise ValueError("max_horizon_hours must be > min_horizon_hours.")
        if not (self.min_horizon_hours <= self.default_horizon_hours <= self.max_horizon_hours):
            raise ValueError("default_horizon_hours must be within min/max horizon bounds.")
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

