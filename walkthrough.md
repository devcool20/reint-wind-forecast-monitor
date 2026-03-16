## 5‑minute walkthrough – outline & script

This document is the script I’ll use for the demo video that REint asks for. It keeps me inside ~5 minutes while touching every important part of the system and analysis.

---

### 0. Setup notes (before recording)

- Have three browser tabs ready:
  - Vercel app (dashboard)
  - Render backend `/docs`
  - GitHub (or local editor) showing the repo
- Optionally have Jupyter open with both notebooks.

Target length: **4:30–5:00 minutes**.

---

### 1. Opening (0:00–0:40)

**Goal:** State the problem in my own words and set expectations.

> “Hi, I’m \<name\>.  
> This is my solution to REint’s Full‑Stack SWE challenge. The task is to build a horizon‑aware dashboard for UK wind power and to analyze how good the forecasts are, and how much wind capacity we can rely on.  
> I’ll first walk through the live app, then briefly show the backend design and API, and I’ll finish with the Jupyter notebooks and my main analytical conclusions.”

---

### 2. Live app demo (0:40–2:15)

**Goal:** Show that the UI solves the challenge cleanly and is easy to reason about.

On the Vercel tab:

> “This is the deployed dashboard. The data source is BMRS, restricted to **January 2024** and `fuelType = WIND`, exactly as described in the prompt.  
> 
> On the left, you choose a **date range** inside January. In the middle, there’s a **forecast horizon slider** from 0 to 48 hours. On the right is a **refresh panel** with manual and auto‑refresh, plus a UTC timestamp for the last successful fetch.
> 
> Below that, I summarise the data as five stats:
> - **Total points** in the selected window  
> - The **applied horizon**  
> - How many points have **actuals**, **forecasts**, and **overlap** where both exist.
> 
> The main chart shows wind generation over time:
> - The **blue line** is actual generation from `FUELHH`.  
> - The **green dashed line with points** is forecast generation from `WINDFOR`.  
> - The **amber markers** are overlap points where we have both a forecast and an actual at the same timestamp, which is where we care about error.
> 
> If I change the horizon to something longer, you can see that the forecast points get **sparser and drift further** from the actual curve. That matches the intuition that longer‑horizon forecasts are both less frequent and less accurate.  
> 
> The tooltips are all in UTC and show MW values, and the layout collapses down nicely on mobile — it becomes a vertical stack of controls, stats, and chart.”

You can briefly switch dev‑tools to a mobile viewport to demonstrate responsiveness.

---

### 3. Backend architecture & data logic (2:15–3:30)

**Goal:** Prove understanding of the data contract and business rules, not just code.

Switch to Render `/docs` or to your editor showing the backend.

> “Behind this is a small **FastAPI** service deployed on Render.
> 
> The key idea is to align BMRS actuals and forecasts on a 30‑minute grid, enforcing the **“latest forecast at least horizon hours before target time”** rule. The main pieces are:
> 
> - `app/core/config.py` – all configuration and business bounds live here: BMRS base URL and timeouts, minimum and maximum horizon (0–48h), the January window, and CORS origins. It uses `pydantic-settings` so everything is validated and driven by environment variables.
> - `app/services/bmrs_client.py` – an async client over `httpx` that talks to the two BMRS endpoints. It chunks large queries into **7‑day windows** to respect API limits and uses connection pooling and timeouts so long ranges don’t break the app.
> - `app/services/forecast_service.py` – this is where the domain logic lives. For each 30‑minute target time:
>   - It looks up all forecasts from `WINDFOR` where `startTime` matches,  
>   - Filters to those whose `publishTime` is ≤ `target_time – horizon`, and  
>   - Picks the **latest such publish time** as the forecast to use.  
>   If we don’t find any forecast for a target, we simply leave the forecast as `null` and only plot the actual.
> - `app/api/forecasts.py` wires this up to `GET /api/forecasts`, validates the query parameters, and returns a typed response with both the **aligned series** and **metadata counts** that the frontend displays.
> 
> Everything is UTC‑normalised, and there’s also a `/health` endpoint and a lightweight root route for Render’s health checks.”

If you have a second, quickly show the OpenAPI `/docs` page and the `GET /api/forecasts` schema.

---

### 4. Frontend structure (3:30–4:05)

**Goal:** Show the React/Next.js side is structured and intentional.

> “On the frontend I use **Next.js with TypeScript**.
> 
> - `src/lib/api.ts` is the only place that knows the backend URL. It reads `NEXT_PUBLIC_BACKEND_URL`, builds the `/api/forecasts` request, and centralises error handling, so the rest of the UI just calls `fetchForecasts`.
> - `src/app/page.tsx` is a single top‑level component that:
>   - tracks the date range, horizon, loading/error state, and auto‑refresh timer,  
>   - calls the API when those change, and  
>   - passes a clean `ForecastResponse` into the chart and stat cards.
> - `src/components/ForecastChart.tsx` converts raw points into Recharts data and renders a **composed chart** – two lines plus a scatter series for overlap points, with a custom tooltip and legend.
> 
> Styling is done with a small set of global CSS rules and CSS variables. The goal was to keep it focused on this one dashboard, but still feel like a real product rather than a throwaway prototype.”

---

### 5. Notebooks & analytical conclusions (4:05–4:50)

**Goal:** Demonstrate own reasoning and that you understood the statistics, not just plotted graphs.

Switch to Jupyter or show the `analysis/` folder.

> “The second half of the challenge is the analysis.
> 
> In `analysis/forecast_error_analysis.ipynb`:
> - I construct error metrics between forecast and actual at the overlap points – both **absolute and signed error**.  
> - I look at **mean, median, and p99** error overall, and then slice it by **forecast horizon** and by **time of day**.  
> - The main pattern I see is \<very short summary of your real finding – for example: median errors are low at short horizons but p99 blows up beyond 24h, and nights/evenings show a slight bias\>.
> 
> In `analysis/reliability_analysis.ipynb`:
> - I only use actual generation and build an **availability curve** for January 2024.  
> - I look at how often different MW levels are exceeded, and use percentiles to decide what “reliable” means in practice.  
> - Based on that, I recommend **\<X\> MW** as a level we can expect to be available at least \<Y\>% of the time, and I discuss the trade‑off between picking a conservative number vs. utilising more of the capacity.
> 
> The notebooks are written so someone else can follow the reasoning step by step, not just read off the final number.”

Adjust the \<X\>/\<Y\> placeholders to match your actual results before recording.

---

### 6. Closing (4:50–5:00)

**Goal:** Tie it together and remind them what you did.

> “To summarise:  
> - I built and deployed a **horizon‑aware wind forecast monitor** that lines up BMRS actuals and forecasts correctly.  
> - I exposed a clean API that the frontend consumes, with validation, sensible defaults, and production‑ready deployment.  
> - And I used Jupyter notebooks to quantify forecast error and reason about reliable wind capacity, explaining the trade‑offs rather than just producing a number.  
> 
> All the links – live app, backend, notebooks, and code – are in the README. Thanks for taking a look.”

