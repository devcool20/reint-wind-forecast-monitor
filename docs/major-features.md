# Major Feature Implementation Notes

## 1) Layered FastAPI structure (api/core/services/models/schemas)
- Description: Separates routing, configuration, integration, domain records, and response contracts for maintainability and testability.
- Why this over alternatives: Chosen over a single-file app to reduce coupling and keep complexity manageable as features scale.

## 2) Typed settings with environment-driven configuration
- Description: Uses `pydantic-settings` for validated runtime config (timeouts, retries, CORS, horizon bounds, date window).
- Why this over alternatives: Chosen over hardcoded constants to support environment parity and safer production configuration changes.

## 3) Robust BMRS client with retry/backoff and strict payload validation
- Description: Wraps BMRS HTTP calls with retriable status handling (429/5xx), exponential backoff, and shape checks.
- Why this over alternatives: Chosen over naive single-shot requests to improve resilience against transient upstream failures.

## 4) Deterministic forecast selection algorithm
- Description: For each target time, selects the latest forecast where `publish_time <= target_time - selected_horizon` and horizon is within 0-48h.
- Why this over alternatives: Chosen over nearest-or-average forecast methods because it directly matches challenge requirements and keeps behavior explainable.

## 5) UTC-normalized datetime handling
- Description: Normalizes all timestamps to UTC and consistently serializes/parses ISO timestamps with `Z`.
- Why this over alternatives: Chosen over mixed/local timezone handling to prevent subtle time-window and horizon bugs.

## 6) Explicit business-rule validation at service boundary
- Description: Rejects invalid ranges (start >= end), out-of-window dates (non-January 2024), and invalid horizon values before data processing.
- Why this over alternatives: Chosen over implicit downstream failures to provide predictable API behavior and cleaner failure modes.

## 7) Container-ready runtime
- Description: Includes a non-root Docker build with deterministic dependency install and uvicorn startup defaults.
- Why this over alternatives: Chosen over local-only execution to enable reproducible deployment in cloud environments.

## 8) Unit tests for core selection logic
- Description: Adds focused tests for latest-valid-forecast selection and horizon-bound filtering correctness.
- Why this over alternatives: Chosen over endpoint-only manual testing to verify core correctness quickly and repeatedly.

