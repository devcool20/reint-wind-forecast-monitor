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
- [ ] Save backend URL: `<to-fill>`

## 4.3 Deploy frontend (Vercel)

- [ ] Create project from `frontend/`.
- [ ] Set env var:
  - `NEXT_PUBLIC_BACKEND_URL=<deployed_backend_url>`
- [ ] Trigger deployment.
- [ ] Verify dashboard works against deployed backend.
- [ ] Save frontend URL: `<to-fill>`

## 4.4 Demo prep

- [ ] Record unlisted video (<=5 minutes).
- [ ] Demonstrate:
  - app usage
  - analysis highlights
  - key recommendation
