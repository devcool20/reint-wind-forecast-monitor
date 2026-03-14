# Step 2: Frontend — Run & verify

Complete every item below. Only move to Step 3 when all are done.

---

## 2.1 Prerequisites

- [ ] **Backend is running** (Step 1 done): `http://localhost:8000` returns 200 for  
  `GET /api/forecasts?start=2024-01-01T00:00:00Z&end=2024-01-02T00:00:00Z&horizon=4`

---

## 2.2 Environment

- [ ] From repo root, go to frontend:
  ```powershell
  cd frontend
  ```
- [ ] Create local env from example:
  ```powershell
  copy .env.example .env.local
  ```
- [ ] Leave `NEXT_PUBLIC_BACKEND_URL=http://localhost:8000` (or set it to your backend URL if different).

---

## 2.3 Install & run

- [ ] Install dependencies:
  ```powershell
  npm install
  ```
- [ ] Start dev server:
  ```powershell
  npm run dev
  ```
- [ ] In browser open: **http://localhost:3000**  
  You should see the UK Wind Forecast Monitor dashboard (hero, date range, horizon slider, chart area).

---

## 2.4 Manual QA (all must pass)

**Filters & data**

- [ ] Change **start date** and **end date** (within Jan 2024). Chart and stats update.
- [ ] Move **Forecast horizon** slider (e.g. 0, 4, 24, 48). Chart and stats update.
- [ ] Pick a range that has data (e.g. 2024-01-01 to 2024-01-03). Chart shows two lines (actual + forecast) and stat cards show numbers.

**Error handling**

- [ ] Stop the backend (Ctrl+C in the backend terminal). In the frontend, change date or horizon or click **Refresh now**. An error panel appears (no crash).
- [ ] Start the backend again. Click **Refresh now** or change a filter. Data loads again.

**Refresh panel**

- [ ] Click **Refresh now**. “Last updated” time changes.
- [ ] Turn **Auto-refresh every 60s** on. Wait ~1 minute; “Last updated” changes again (optional: leave off if you prefer).

**Responsive**

- [ ] Resize the browser to a narrow width (~375px). Layout stacks; date pickers and slider remain usable; chart is readable (scroll if needed).

---

## 2.5 Build check (optional but recommended)

- [ ] From `frontend` directory:
  ```powershell
  npm run lint
  npm run build
  ```
  Both finish without errors.

---

## Step 2 complete

When every checkbox above is done, Step 2 is complete. You can then move to **Step 3 (analysis notebooks)**.
