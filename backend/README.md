# Backend (Phase 1)
Production-grade FastAPI backend for UK wind generation actual vs forecast monitoring.

## What this backend does
- Pulls **actual generation** data from BMRS `FUELHH`.
- Pulls **forecast generation** data from BMRS `WINDFOR`.
- Applies forecast selection rule: for each target time, pick the **latest forecast published at least `horizon` hours before target**.
- Enforces challenge window: January 2024 only, with forecast horizons in 0-48 hours.

## Local setup
1. Create and activate a virtual environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Copy env template:
   - `copy .env.example .env` (Windows)
4. Run API:
   - `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

## Endpoints
- `GET /health`
- `GET /api/forecasts?start=2024-01-01T00:00:00Z&end=2024-01-02T00:00:00Z&horizon=4`

## Notes on BMRS filters
This backend uses BMRS date filters `publishDateTimeFrom` and `publishDateTimeTo` on `https://data.elexon.co.uk/bmrs/api/v1/datasets/<DATASET>` for historical retrieval.

