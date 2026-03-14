# Wind Power Forecast Monitoring System
## Goal
Build a full-stack application to visualize UK wind power generation forecasts vs actuals, with backend API for data fetching and frontend React application.
## Tech Stack
* **Frontend**: TypeScript, React, Next.js (for easy deployment), Chart.js/Recharts for visualization, TailwindCSS
* **Backend**: Python, FastAPI, Pandas for data processing
* **Deployment**: Vercel (frontend) + Railway/Render (backend API)
## Architecture
### Project Structure
```warp-runnable-command
wind-forecast-monitor/
├── frontend/                 # Next.js React app
│   ├── app/
│   │   ├── page.tsx         # Main dashboard
│   │   ├── layout.tsx       # Root layout
│   │   └── globals.css      # Tailwind styles
│   ├── components/
│   │   ├── ForecastChart.tsx       # Time series chart
│   │   ├── DateRangePicker.tsx     # Calendar widgets
│   │   ├── HorizonSlider.tsx       # Forecast horizon slider
│   │   └── LoadingSpinner.tsx
│   ├── lib/
│   │   ├── api.ts           # API client
│   │   └── types.ts         # TypeScript interfaces
│   └── package.json
├── backend/                 # FastAPI backend
│   ├── main.py              # FastAPI app entry point
│   ├── api/
│   │   └── forecasts.py     # Forecast endpoints
│   ├── services/
│   │   ├── data_fetcher.py  # Elexon API client
│   │   └── data_processor.py # Data processing logic
│   ├── models/
│   │   └── forecast_model.py  # Pydantic models
│   ├── requirements.txt
│   └── Dockerfile
├── analysis/                # Jupyter notebooks
│   ├── forecast_error_analysis.ipynb
│   └── reliability_analysis.ipynb
├── README.md
└── .gitignore
```
## Implementation Plan
### Phase 1: Backend Setup
1. Initialize FastAPI project structure
2. Create Elexon API client to fetch actual generation data (FUELHH endpoint)
3. Create Elexon API client to fetch forecast data (WINDFOR endpoint)
4. Implement data processing:
    * Filter by fuelType 'WIND' for actuals
    * Filter by date range (January 2024)
    * Filter by forecast horizon (0-48 hours)
    * Filter by publish time (latest forecast before target time - horizon)
    * Handle 30-minute resolution
5. Create API endpoints:
    * GET /api/forecasts?start=DATE&end=DATE&horizon=HOURS
    * Return merged actual + forecast data
6. Add CORS support for frontend
7. Create Dockerfile and deployment configuration
### Phase 2: Frontend Setup
1. Initialize Next.js project with TypeScript, TailwindCSS
2. Create basic layout with header/footer
3. Implement DateRangePicker component
4. Implement HorizonSlider component
5. Integrate Chart.js/Recharts for time series visualization
6. Create API client to fetch data from backend
7. Add loading states and error handling
8. Implement responsive design (mobile + web)
9. Add chart tooltips and legends
### Phase 3: Analysis Notebooks
1. forecast_error_analysis.ipynb:
    * Calculate error metrics (mean, median, p99)
    * Analyze error by forecast horizon
    * Analyze error by time of day
    * Visualize distributions and trends
2. reliability_analysis.ipynb:
    * Analyze historical wind generation patterns
    * Assess consistency and availability
    * Make MW recommendation with confidence intervals
    * Document reasoning and evidence
### Phase 4: Testing & Deployment
1. Test backend endpoints with sample queries
2. Test frontend with different date ranges and horizon values
3. Verify mobile responsiveness
4. Deploy backend to Railway/Render
5. Deploy frontend to Vercel with environment variable for backend URL
6. Test deployed application
7. Create comprehensive README
8. Record demo video (≤5 minutes)
### Phase 5: Submission
1. Create Git repo with commit history
2. Zip including .git directory
3. Upload to Google Drive
4. Send email to hiring@reint.ai with required details
## Key Considerations
* Elexon API returns streaming data - need to buffer and parse efficiently
* Handle missing forecast data (ignore and don't plot)
* Forecast horizon calculation: targetTime - publishTime
* "Latest forecast before" means max(publishTime) where targetTime - publishTime >= horizon
* Date formats in API need proper parsing
* 30-minute resolution means 48 data points per day
* Both January 2024 and configurable date ranges needed
## Optional Enhancements
* Add error visualization (shaded region around forecast)
* Include summary statistics (MAE, RMSE) on dashboard
* Allow export of chart as image
* Add data table view for detailed inspection
* Cache API responses to reduce calls
