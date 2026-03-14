# Frontend (Phase 2)

Next.js + TypeScript dashboard for comparing UK wind generation actuals vs forecast values across date ranges and forecast horizons.

## Features

- Date range picker constrained to January 2024
- Forecast horizon slider (0-48 hours)
- Recharts time series with tooltip and legend
- Loading, error, and empty-state UX
- Optional auto-refresh every 60 seconds

## Prerequisites

- Node.js 20+
- Backend API running (FastAPI service in `../backend`)

## Environment

Create `frontend/.env.local`:

```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

If omitted, the app defaults to `http://localhost:8000`.

## Run Locally

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Build & Lint

```bash
npm run lint
npm run build
```
