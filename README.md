## Overview

This repo contains my submission for the **REint Full‑Stack SWE challenge**.

The goal is to:
- Build a **forecast monitoring app** for UK wind power, showing actual vs forecast generation for January 2024, and
- Produce **analysis notebooks** that quantify forecast error and answer: *“How much wind capacity can we rely on?”*

The stack is:
- **Backend** – Python, FastAPI, `httpx`, Pandas, Docker (deployed on Render)
- **Frontend** – TypeScript, Next.js (App Router), Recharts (deployed on Vercel)
- **Analysis** – Jupyter, Pandas/NumPy/Seaborn

## Layout

- `backend/` – FastAPI service talking to BMRS (`FUELHH` for actuals, `WINDFOR` for forecasts) and exposing `/api/forecasts`.
- `frontend/` – Next.js dashboard with date range, horizon slider, stats cards, and chart.
- `analysis/` – Two notebooks: forecast error analysis and wind reliability recommendation.
- `docs/` – Short checklists for frontend, analysis, deployment, and submission.

## What the app does

- **Aligns BMRS actuals and forecasts**
  - Pulls January 2024 data for `fuelType == "WIND"` from `FUELHH` (actual generation).
  - Pulls matching `WINDFOR` forecasts.
  - For each 30‑minute target time, selects the **latest forecast** whose `publishTime` is at most `target_time – horizon` and whose effective horizon is in \[0, 48] hours.
  - If there is no valid forecast for a target time, that point is left as “actual‑only” and is not plotted as a forecast.

- **Serves a simple, explicit API**
  - `GET /api/forecasts?start=ISO&end=ISO&horizon=H`  
    Returns:
    - `metadata` (counts of total/actual/forecast/overlap points)
    - `forecast_horizon_hours`
    - Aligned point series with `actual_generation_mw` and `forecast_generation_mw`.
  - Validates:
    - Dates are inside January 2024.
    - `start <= end`.
    - `horizon` in \[0, 48].

- **Visualizes the data clearly**
  - Date range picker, horizon slider, manual and auto refresh.
  - Main chart:
    - Blue line – actual generation.
    - Green dashed line + points – forecast generation.
    - Amber markers – overlap points where both series exist at the same timestamp.
  - Stats row summarizing total, applied horizon, and coverage (actuals / forecasts / overlaps).
  - Designed to work cleanly on both desktop and mobile.

## Local development

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Quick sanity check:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/forecasts?start=2024-01-01T00:00:00Z&end=2024-01-02T00:00:00Z&horizon=4"
```

### Frontend

```powershell
cd frontend
copy .env.example .env.local
npm install
npm run dev
```

Then open `http://localhost:3000`.

## Tests and quality checks

### Backend

```powershell
cd backend
pytest
```

### Frontend

```powershell
cd frontend
npm run lint
npm run build
```

## Analysis notebooks

Backend needs to be reachable at `http://localhost:8000` (or you can hard‑code the Render URL in the notebooks if desired).

```powershell
cd analysis
jupyter lab
```

Notebooks:
- `forecast_error_analysis.ipynb` – error distributions (mean/median/p99), behaviour by horizon, and time‑of‑day patterns.
- `reliability_analysis.ipynb` – historical wind generation, availability curve, and MW recommendation with rationale.

## Deployment

- **Backend** – Dockerized FastAPI on Render:
  - Start command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Important env vars: `CORS_ALLOW_ORIGINS`, horizon bounds, January window (see `backend/.env.example`).
- **Frontend** – Next.js app on Vercel:
  - Root directory: `frontend`
  - Env: `NEXT_PUBLIC_BACKEND_URL=<Render backend URL>`


## Links (to be filled before submission)

- App demo: `https://reint-wind-forecast-monitor.vercel.app/`
- Backend API: `https://reint-wind-forecast-api.onrender.com`
- Demo video: `<unlisted-youtube-url>`
- Repo zip (with `.git`): `<google-drive-url>`

## AI tools

I used AI assistance (Cursor / GPT‑style tools) for:
- Boilerplate generation (FastAPI/Next.js wiring, CSS scaffolding)
- Refactoring suggestions and debugging help
- Drafting documentation, which I then edited by hand.
