# Step 3: Analysis Notebooks — Run & finalize

Complete this step only after Step 2 is fully complete.

## 3.1 Prerequisites

- [ ] Backend is running on `http://localhost:8000`.
- [ ] Jupyter is installed in an environment with: `pandas`, `numpy`, `matplotlib`, `seaborn`, `requests`.

## 3.2 Open notebooks

- [ ] From repo root:
  ```powershell
  cd analysis
  jupyter lab
  ```
- [ ] Open:
  - `forecast_error_analysis.ipynb`
  - `reliability_analysis.ipynb`

## 3.3 Forecast error notebook completion

- [ ] Run all cells top-to-bottom.
- [ ] Confirm outputs render for:
  - overall metrics (mean/median/p99/RMSE)
  - horizon-wise metrics
  - time-of-day grouped metrics
  - plots
- [ ] Replace interpretation template with your own reasoning and concrete values.

## 3.4 Reliability notebook completion

- [ ] Run all cells top-to-bottom.
- [ ] Confirm outputs render for:
  - summary stats
  - availability curve
  - bootstrap CI
  - recommendation variable
- [ ] Replace recommendation template with your own final text using computed values.

## 3.5 Done criteria

- [ ] Both notebooks execute without errors.
- [ ] Both notebooks contain final written interpretation/recommendation, not placeholders.
