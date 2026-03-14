from __future__ import annotations

import json
from dataclasses import dataclass

import numpy as np
import pandas as pd
import requests

API_BASE_URL = "http://localhost:8010"
START_ISO = "2024-01-01T00:00:00Z"
END_ISO = "2024-01-31T23:30:00Z"
HORIZONS = [0, 2, 4, 8, 12, 24, 36, 48]


@dataclass
class ChunkResult:
    horizon: int
    status: int
    start: str
    end: str


def iso_z(ts: pd.Timestamp) -> str:
    return ts.isoformat().replace("+00:00", "Z")


def fetch_horizon_df(horizon: int) -> tuple[pd.DataFrame, list[ChunkResult]]:
    response = requests.get(
        f"{API_BASE_URL}/api/forecasts",
        params={"start": START_ISO, "end": END_ISO, "horizon": horizon},
        timeout=180,
    )
    chunks = [
        ChunkResult(
            horizon=horizon,
            status=response.status_code,
            start=START_ISO,
            end=END_ISO,
        )
    ]
    if response.status_code != 200:
        return pd.DataFrame(), chunks

    points = response.json().get("points", [])
    if not points:
        return pd.DataFrame(), chunks

    df = pd.DataFrame(points).drop_duplicates(subset=["target_time"])
    df["target_time"] = pd.to_datetime(df["target_time"], utc=True)
    df["requested_horizon"] = horizon
    return df, chunks


def compute_forecast_error_metrics() -> dict:
    all_frames: list[pd.DataFrame] = []
    all_chunks: list[ChunkResult] = []

    for h in HORIZONS:
        df_h, chunks = fetch_horizon_df(h)
        all_chunks.extend(chunks)
        if not df_h.empty:
            all_frames.append(df_h)

    if not all_frames:
        return {"ok": False, "reason": "No horizon data fetched", "chunks": [c.__dict__ for c in all_chunks]}

    merged = pd.concat(all_frames, ignore_index=True)
    merged = merged.dropna(subset=["actual_generation_mw", "forecast_generation_mw"]).copy()
    merged["error_mw"] = merged["forecast_generation_mw"] - merged["actual_generation_mw"]
    merged["abs_error_mw"] = merged["error_mw"].abs()
    merged["squared_error"] = merged["error_mw"] ** 2
    merged["hour_utc"] = merged["target_time"].dt.hour

    overall = {
        "mean_error_mw": float(round(merged["error_mw"].mean(), 2)),
        "median_error_mw": float(round(merged["error_mw"].median(), 2)),
        "mean_abs_error_mw": float(round(merged["abs_error_mw"].mean(), 2)),
        "median_abs_error_mw": float(round(merged["abs_error_mw"].median(), 2)),
        "p99_abs_error_mw": float(round(merged["abs_error_mw"].quantile(0.99), 2)),
        "rmse_mw": float(round(float(np.sqrt(merged["squared_error"].mean())), 2)),
        "rows": int(len(merged)),
    }

    horizon_metrics = (
        merged.groupby("requested_horizon", as_index=False)
        .agg(
            sample_size=("abs_error_mw", "size"),
            mean_abs_error_mw=("abs_error_mw", "mean"),
            median_abs_error_mw=("abs_error_mw", "median"),
            p99_abs_error_mw=("abs_error_mw", lambda s: s.quantile(0.99)),
            rmse_mw=("squared_error", lambda s: np.sqrt(s.mean())),
        )
        .sort_values("requested_horizon")
    )
    for col in ["mean_abs_error_mw", "median_abs_error_mw", "p99_abs_error_mw", "rmse_mw"]:
        horizon_metrics[col] = horizon_metrics[col].round(2)

    h4 = horizon_metrics[horizon_metrics["requested_horizon"] == 4]
    h24 = horizon_metrics[horizon_metrics["requested_horizon"] == 24]
    h48 = horizon_metrics[horizon_metrics["requested_horizon"] == 48]

    tod = (
        merged.groupby(["requested_horizon", "hour_utc"], as_index=False)["abs_error_mw"]
        .mean()
        .rename(columns={"abs_error_mw": "mean_abs_error_mw"})
    )

    peak_hour_row = tod.sort_values("mean_abs_error_mw", ascending=False).iloc[0]

    return {
        "ok": True,
        "overall": overall,
        "horizon_metrics": horizon_metrics.to_dict(orient="records"),
        "h4": h4.to_dict(orient="records"),
        "h24": h24.to_dict(orient="records"),
        "h48": h48.to_dict(orient="records"),
        "peak_hour": {
            "horizon": int(peak_hour_row["requested_horizon"]),
            "hour_utc": int(peak_hour_row["hour_utc"]),
            "mae_mw": float(round(peak_hour_row["mean_abs_error_mw"], 2)),
        },
        "chunks": [c.__dict__ for c in all_chunks],
    }


def compute_reliability_metrics() -> dict:
    # Reuse horizon=4 chunks to get full actual series.
    df, chunks = fetch_horizon_df(4)
    if df.empty:
        return {"ok": False, "reason": "No reliability data fetched", "chunks": [c.__dict__ for c in chunks]}

    actual_df = df.dropna(subset=["actual_generation_mw"]).copy()
    actual_df["target_time"] = pd.to_datetime(actual_df["target_time"], utc=True)
    actual_df = actual_df[["target_time", "actual_generation_mw"]].drop_duplicates().sort_values("target_time")
    actual_df["hour_utc"] = actual_df["target_time"].dt.hour

    sample = actual_df["actual_generation_mw"].to_numpy()
    rng = np.random.default_rng(42)
    boot_iterations = 2000
    boot_p10 = np.empty(boot_iterations)
    for i in range(boot_iterations):
        boot_sample = rng.choice(sample, size=sample.shape[0], replace=True)
        boot_p10[i] = np.quantile(boot_sample, 0.10)

    p10_point = float(np.quantile(sample, 0.10))
    p10_ci_low = float(np.quantile(boot_p10, 0.025))
    p10_ci_high = float(np.quantile(boot_p10, 0.975))
    recommendation_mw = int(round(p10_point, -1))

    summary = {
        "mean_mw": float(round(actual_df["actual_generation_mw"].mean(), 2)),
        "median_mw": float(round(actual_df["actual_generation_mw"].median(), 2)),
        "std_mw": float(round(actual_df["actual_generation_mw"].std(), 2)),
        "p01_mw": float(round(actual_df["actual_generation_mw"].quantile(0.01), 2)),
        "p05_mw": float(round(actual_df["actual_generation_mw"].quantile(0.05), 2)),
        "p10_mw": float(round(p10_point, 2)),
        "p25_mw": float(round(actual_df["actual_generation_mw"].quantile(0.25), 2)),
        "rows": int(len(actual_df)),
    }

    hourly = (
        actual_df.groupby("hour_utc", as_index=False)["actual_generation_mw"]
        .agg(
            mean_mw="mean",
            median_mw="median",
            p10_mw=lambda s: s.quantile(0.10),
        )
        .sort_values("hour_utc")
    )
    low_hour = hourly.sort_values("p10_mw").iloc[0]
    high_hour = hourly.sort_values("p10_mw", ascending=False).iloc[0]

    return {
        "ok": True,
        "summary": summary,
        "p10_ci": [float(round(p10_ci_low, 2)), float(round(p10_ci_high, 2))],
        "recommendation_mw": recommendation_mw,
        "hourly_low": {"hour_utc": int(low_hour["hour_utc"]), "p10_mw": float(round(low_hour["p10_mw"], 2))},
        "hourly_high": {"hour_utc": int(high_hour["hour_utc"]), "p10_mw": float(round(high_hour["p10_mw"], 2))},
        "chunks": [c.__dict__ for c in chunks],
    }


if __name__ == "__main__":
    output = {
        "forecast_error": compute_forecast_error_metrics(),
        "reliability": compute_reliability_metrics(),
    }
    print(json.dumps(output, indent=2))
