"use client";

import { useEffect, useMemo, useState } from "react";

import { DateRangePicker } from "@/components/DateRangePicker";
import { ForecastChart } from "@/components/ForecastChart";
import { HorizonSlider } from "@/components/HorizonSlider";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { fetchForecasts } from "@/lib/api";
import type { ForecastResponse } from "@/lib/types";

const MIN_DATE = "2024-01-01";
const MAX_DATE = "2024-01-31";

function toRangeStartIso(date: string): string {
  return `${date}T00:00:00Z`;
}

function toRangeEndIso(date: string): string {
  return `${date}T23:30:00Z`;
}

export default function Home() {
  const [startDate, setStartDate] = useState("2024-01-01");
  const [endDate, setEndDate] = useState("2024-01-03");
  const [horizon, setHorizon] = useState(4);
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(false);
  const [refreshTick, setRefreshTick] = useState(0);

  const [data, setData] = useState<ForecastResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdatedUtc, setLastUpdatedUtc] = useState<string | null>(null);

  const invalidRange = useMemo(() => startDate > endDate, [startDate, endDate]);
  const lastUpdatedLabel = useMemo(() => {
    if (!lastUpdatedUtc) {
      return null;
    }
    return new Intl.DateTimeFormat("en-GB", {
      month: "short",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
      timeZone: "UTC",
    }).format(new Date(lastUpdatedUtc));
  }, [lastUpdatedUtc]);

  useEffect(() => {
    if (!autoRefreshEnabled) {
      return;
    }

    const timerId = setInterval(() => {
      setRefreshTick((value) => value + 1);
    }, 60_000);

    return () => clearInterval(timerId);
  }, [autoRefreshEnabled]);

  useEffect(() => {
    if (invalidRange) {
      setError("Start date must be before or equal to end date.");
      setData(null);
      return;
    }

    let cancelled = false;

    async function runFetch() {
      setLoading(true);
      setError(null);
      try {
        const response = await fetchForecasts({
          start: toRangeStartIso(startDate),
          end: toRangeEndIso(endDate),
          horizon,
        });
        if (!cancelled) {
          setData(response);
          setLastUpdatedUtc(new Date().toISOString());
        }
      } catch (caughtError) {
        if (!cancelled) {
          const message =
            caughtError instanceof Error
              ? caughtError.message
              : "Failed to fetch forecast data from backend.";
          setError(message);
          setData(null);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void runFetch();

    return () => {
      cancelled = true;
    };
  }, [startDate, endDate, horizon, invalidRange, refreshTick]);

  return (
    <main className="page-shell">
      <section className="hero">
        <p className="eyebrow">Phase 2 Dashboard</p>
        <h1>UK Wind Forecast Monitor</h1>
        <p className="muted">
          Compare actual generation against selected forecast points by date range and horizon.
        </p>
      </section>

      <section className="controls-grid">
        <DateRangePicker
          startDate={startDate}
          endDate={endDate}
          onStartDateChange={setStartDate}
          onEndDateChange={setEndDate}
          minDate={MIN_DATE}
          maxDate={MAX_DATE}
        />
        <HorizonSlider horizon={horizon} onHorizonChange={setHorizon} />
        <section className="panel">
          <h2 className="panel-title">Refresh</h2>
          <label className="toggle-row" htmlFor="auto-refresh">
            <input
              id="auto-refresh"
              type="checkbox"
              checked={autoRefreshEnabled}
              onChange={(event) => setAutoRefreshEnabled(event.target.checked)}
            />
            <span>Auto-refresh every 60s</span>
          </label>
          <button className="button" type="button" onClick={() => setRefreshTick((value) => value + 1)}>
            Refresh now
          </button>
          <p className="muted small">
            Last updated: {lastUpdatedLabel ? `${lastUpdatedLabel} UTC` : "waiting for first successful fetch"}
          </p>
        </section>
      </section>

      {error ? (
        <section className="panel error-panel">
          <h2 className="panel-title">Request Error</h2>
          <p>{error}</p>
        </section>
      ) : null}

      {loading ? <LoadingSpinner /> : null}

      {!loading && data ? (
        <>
          {data.metadata.points_total === 0 ? (
            <section className="panel info-panel">
              <h2 className="panel-title">No data for current filters</h2>
              <p className="muted">
                Try a wider date range or lower horizon. If this persists, confirm the backend service is running
                and reachable from the frontend.
              </p>
            </section>
          ) : null}
          <section className="stats-grid">
            <article className="stat-card">
              <span className="stat-label">Total points</span>
              <strong>{data.metadata.points_total}</strong>
            </article>
            <article className="stat-card">
              <span className="stat-label">Applied horizon</span>
              <strong>{data.forecast_horizon_hours}h</strong>
            </article>
            <article className="stat-card">
              <span className="stat-label">With actuals</span>
              <strong>{data.metadata.points_with_actual}</strong>
            </article>
            <article className="stat-card">
              <span className="stat-label">With forecasts</span>
              <strong>{data.metadata.points_with_forecast}</strong>
            </article>
            <article className="stat-card">
              <span className="stat-label">Overlap points</span>
              <strong>{data.metadata.points_with_both}</strong>
            </article>
          </section>
          <ForecastChart points={data.points} appliedHorizonHours={data.forecast_horizon_hours} />
        </>
      ) : null}
      </main>
  );
}
