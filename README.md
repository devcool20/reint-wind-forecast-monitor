# REint Wind Forecast Monitor

Full-stack challenge submission for monitoring UK wind generation forecasts vs actuals, plus analysis notebooks for forecast error and wind reliability.

## Project Structure

- `backend/` - FastAPI API that fetches BMRS datasets and returns merged actual-vs-forecast series.
- `frontend/` - Next.js dashboard with date-range, horizon slider, charting, and refresh controls.
- `analysis/` - Jupyter notebooks for forecast-error analysis and reliability recommendation.
- `docs/` - Step-by-step execution checklists.

## Features Implemented

### Backend (Phase 1)

- BMRS integration for `FUELHH` (actual) and `WINDFOR` (forecast).
- Forecast selection rule: latest forecast published at least `horizon` hours before target.
- Validation:
  - January 2024 date window only.
  - Horizon bounds: 0-48 hours.
  - Invalid input errors with clear messages.
- CORS configuration via env.
- Health endpoint and forecasts endpoint.
- Unit tests for core forecast-selection logic.

### Frontend (Phase 2)

- Responsive dashboard layout with header/footer.
- Date range picker and horizon slider controls.
- Recharts line chart with tooltip and legend.
- Stats cards for coverage metadata.
- Loading, error, and empty-data states.
- Manual refresh + optional auto-refresh every 60 seconds.

### Analysis (Phase 3)

- `analysis/forecast_error_analysis.ipynb`
  - mean/median/p99 and RMSE metrics
  - horizon-wise error behavior
  - time-of-day error behavior
- `analysis/reliability_analysis.ipynb`
  - historical actual wind generation summary
  - availability curve
  - bootstrap CI around P10 reliability estimate
  - MW recommendation scaffold with caveats

## Local Setup

### 1) Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Quick test:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/forecasts?start=2024-01-01T00:00:00Z&end=2024-01-02T00:00:00Z&horizon=4"
```

### 2) Frontend

```powershell
cd frontend
copy .env.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`.

## Quality Checks

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

## Running Analysis Notebooks

Backend must be running locally (`http://localhost:8000`).

```powershell
cd analysis
jupyter lab
```

Then execute:

- `forecast_error_analysis.ipynb`
- `reliability_analysis.ipynb`

## Deployment (Phase 4)

- Deploy backend on Railway/Render.
- Deploy frontend on Vercel and set:
  - `NEXT_PUBLIC_BACKEND_URL=<deployed_backend_url>`

Use detailed checklists:

- `docs/STEP2-FRONTEND.md`
- `docs/STEP3-ANALYSIS.md`
- `docs/STEP4-DEPLOYMENT.md`
- `docs/STEP5-SUBMISSION.md`

## Submission Placeholders

- App demo link: `<to-fill>`
- Demo video link: `<to-fill>`
- Repo zip (with `.git`) link: `<to-fill>`

## AI Tool Disclosure

AI coding assistance was used for implementation acceleration, debugging support, and documentation drafting. Final code, validation, and analysis interpretation were reviewed manually.
