from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

import httpx

from app.core.config import Settings
from app.core.datetime_utils import to_iso_z

logger = logging.getLogger(__name__)


class BMRSClientError(RuntimeError):
    """Raised when BMRS requests fail after retries or return unexpected payloads."""


class BMRSClient:
    def __init__(self, settings: Settings, http_client: httpx.AsyncClient) -> None:
        self._settings = settings
        self._http_client = http_client
        self._base_url = settings.bmrs_base_url.rstrip("/")

    async def fetch_actual_generation(
        self,
        publish_from: datetime,
        publish_to: datetime,
    ) -> list[dict[str, Any]]:
        return await self._get_dataset_chunked(
            "FUELHH",
            publish_from=publish_from,
            publish_to=publish_to,
            extra_params={"fuelType": "WIND"},
        )

    async def fetch_forecast_generation(
        self,
        publish_from: datetime,
        publish_to: datetime,
    ) -> list[dict[str, Any]]:
        return await self._get_dataset_chunked(
            "WINDFOR",
            publish_from=publish_from,
            publish_to=publish_to,
            extra_params={},
        )

    async def _get_dataset_chunked(
        self,
        dataset: str,
        *,
        publish_from: datetime,
        publish_to: datetime,
        extra_params: dict[str, str],
    ) -> list[dict[str, Any]]:
        """
        BMRS enforces max 7-day query windows for some datasets.
        Query in <=7 day chunks and merge responses.
        """
        rows: list[dict[str, Any]] = []
        for chunk_from, chunk_to in self._iter_chunk_ranges(publish_from, publish_to):
            params = {
                "publishDateTimeFrom": to_iso_z(chunk_from),
                "publishDateTimeTo": to_iso_z(chunk_to),
                **extra_params,
            }
            chunk_rows = await self._get_dataset(dataset, params)
            rows.extend(chunk_rows)
        return rows

    @staticmethod
    def _iter_chunk_ranges(
        publish_from: datetime,
        publish_to: datetime,
    ) -> list[tuple[datetime, datetime]]:
        if publish_to < publish_from:
            return []

        max_span_inclusive = timedelta(days=7) - timedelta(minutes=30)
        ranges: list[tuple[datetime, datetime]] = []
        current = publish_from
        while current <= publish_to:
            chunk_end = min(current + max_span_inclusive, publish_to)
            ranges.append((current, chunk_end))
            current = chunk_end + timedelta(minutes=30)
        return ranges

    async def _get_dataset(
        self,
        dataset: str,
        params: dict[str, str],
    ) -> list[dict[str, Any]]:
        url = f"{self._base_url}/datasets/{dataset}"
        max_attempts = self._settings.bmrs_max_retries + 1

        for attempt in range(1, max_attempts + 1):
            try:
                response = await self._http_client.get(
                    url,
                    params=params,
                    headers={"Accept": "application/json"},
                )

                if response.status_code in {429, 500, 502, 503, 504}:
                    raise httpx.HTTPStatusError(
                        "Retriable upstream status",
                        request=response.request,
                        response=response,
                    )

                response.raise_for_status()
                payload = response.json()

                if isinstance(payload, dict):
                    data = payload.get("data")
                    if isinstance(data, list):
                        return data
                if isinstance(payload, list):
                    return payload

                raise BMRSClientError(
                    f"Unexpected payload format from {dataset}: {type(payload).__name__}"
                )

            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code if exc.response is not None else None
                if status_code not in {429, 500, 502, 503, 504}:
                    raise BMRSClientError(
                        f"Non-retriable HTTP error from BMRS ({status_code}) for {dataset}."
                    ) from exc
                if attempt == max_attempts:
                    raise BMRSClientError(
                        f"BMRS HTTP error after retries for {dataset}: {status_code}"
                    ) from exc
                await self._sleep_backoff(attempt, dataset, exc)

            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                if attempt == max_attempts:
                    raise BMRSClientError(
                        f"BMRS network timeout/error after retries for {dataset}."
                    ) from exc
                await self._sleep_backoff(attempt, dataset, exc)

            except ValueError as exc:
                raise BMRSClientError(f"Invalid JSON received from BMRS for {dataset}.") from exc

        raise BMRSClientError(f"Exhausted retries while fetching dataset {dataset}.")

    async def _sleep_backoff(
        self,
        attempt: int,
        dataset: str,
        exc: Exception,
    ) -> None:
        delay_seconds = self._settings.bmrs_backoff_seconds * (2 ** (attempt - 1))
        logger.warning(
            "BMRS request failed (attempt %s) for %s; retrying in %.2fs. Error: %s",
            attempt,
            dataset,
            delay_seconds,
            exc,
        )
        await asyncio.sleep(delay_seconds)

