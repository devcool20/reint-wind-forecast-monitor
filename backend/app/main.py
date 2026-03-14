from __future__ import annotations

from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.forecasts import router as forecasts_router
from app.api.health import router as health_router
from app.core.config import Settings, get_settings
from app.core.logging_config import configure_logging
from app.services.bmrs_client import BMRSClient
from app.services.forecast_service import ForecastService


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings: Settings = get_settings()
    configure_logging(settings.log_level)

    timeout = httpx.Timeout(
        settings.bmrs_timeout_seconds,
        connect=settings.bmrs_timeout_seconds,
    )
    limits = httpx.Limits(max_connections=20, max_keepalive_connections=10)

    async with httpx.AsyncClient(timeout=timeout, limits=limits) as http_client:
        app.state.settings = settings
        app.state.bmrs_client = BMRSClient(settings=settings, http_client=http_client)
        app.state.forecast_service = ForecastService(
            settings=settings,
            bmrs_client=app.state.bmrs_client,
        )
        yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["GET", "OPTIONS"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(forecasts_router)

    return app


app = create_app()

