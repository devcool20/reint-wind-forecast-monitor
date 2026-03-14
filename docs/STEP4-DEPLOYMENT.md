# Step 4: Testing & Deployment

Complete this step only after Steps 1-3 are fully complete.

## 4.1 Final local validation

- [ ] Backend tests:
  ```powershell
  cd backend
  pytest
  ```
- [ ] Frontend checks:
  ```powershell
  cd frontend
  npm run lint
  npm run build
  ```
- [ ] Manual frontend QA confirmed (filters, slider, errors, mobile).

## 4.2 Deploy backend (Railway/Render)

- [ ] Create service from `backend/`.
- [ ] Install command: `pip install -r requirements.txt`.
- [ ] Start command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
- [ ] Set env vars as needed (copy from `.env.example`).
- [ ] Verify endpoint:
  - `GET /health`
  - `GET /api/forecasts?...`
- [ ] Save backend URL: `https://reint-wind-forecast-api.onrender.com`

## 4.3 Deploy frontend (Vercel)

- [ ] Push latest code (frontend in repo root under `frontend/`).
- [ ] Go to [vercel.com](https://vercel.com) → **Add New** → **Project**.
- [ ] Import your Git repo (`reint-wind-forecast-monitor`).
- [ ] **Root Directory:** set to `frontend` (click Edit, enter `frontend`).
- [ ] **Environment Variable:** add:
  - Name: `NEXT_PUBLIC_BACKEND_URL`
  - Value: `https://reint-wind-forecast-api.onrender.com`
  - Apply to Production (and Preview if you want).
- [ ] Deploy. Wait for build to finish.
- [ ] Open the deployed URL and verify: date range, horizon slider, chart loads from API.
- [ ] **Backend CORS:** In Render → your backend service → **Environment**, add or set:
  - `CORS_ALLOW_ORIGINS` = your Vercel URL (e.g. `https://reint-wind-forecast-monitor.vercel.app`)  
  Or use `*` to allow any origin (simpler, less strict).
- [ ] Save frontend URL: `<to-fill>`

## 4.4 Demo prep

- [ ] Record unlisted video (<=5 minutes).
- [ ] Demonstrate:
  - app usage
  - analysis highlights
  - key recommendation
