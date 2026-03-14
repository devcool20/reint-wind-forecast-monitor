"use client";

import {
  ComposedChart,
  CartesianGrid,
  Legend,
  Line,
  ResponsiveContainer,
  Scatter,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { ForecastPoint } from "@/lib/types";

type ForecastChartProps = {
  points: ForecastPoint[];
  appliedHorizonHours?: number;
};

type ChartPoint = {
  targetTimeLabel: string;
  targetTimestamp: string;
  actual: number | null;
  forecast: number | null;
  overlap: number | null;
};

const numberFormatter = new Intl.NumberFormat("en-GB", {
  maximumFractionDigits: 0,
});

const dateTimeFormatter = new Intl.DateTimeFormat("en-GB", {
  month: "short",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
  timeZone: "UTC",
});

function buildChartData(points: ForecastPoint[]): ChartPoint[] {
  return points.map((point) => ({
    targetTimeLabel: dateTimeFormatter.format(new Date(point.target_time)),
    targetTimestamp: point.target_time,
    actual: point.actual_generation_mw,
    forecast: point.forecast_generation_mw,
    overlap:
      point.actual_generation_mw !== null && point.forecast_generation_mw !== null
        ? point.actual_generation_mw
        : null,
  }));
}

export function ForecastChart({ points, appliedHorizonHours }: ForecastChartProps) {
  const data = buildChartData(points);
  const forecastPointCount = data.filter((point) => point.forecast !== null).length;
  const actualPointCount = data.filter((point) => point.actual !== null).length;
  const overlapPointCount = data.filter((point) => point.overlap !== null).length;

  if (data.length === 0) {
    return (
      <section className="panel chart-panel">
        <h2 className="panel-title">Wind Generation Series</h2>
        <p className="muted">No points returned for this date range and horizon.</p>
      </section>
    );
  }

  return (
    <section className="panel chart-panel">
      <h2 className="panel-title">Wind Generation Series</h2>
      <p className="muted small">
        Applied horizon: {appliedHorizonHours ?? "-"}h | Actual points: {actualPointCount} | Forecast points:{" "}
        {forecastPointCount} | Overlap points: {overlapPointCount}
      </p>
      <div className="chart-wrap">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 20, right: 20, left: 0, bottom: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.12)" />
            <XAxis
              dataKey="targetTimeLabel"
              minTickGap={28}
              tick={{ fill: "#a3adc2", fontSize: 12 }}
              tickMargin={8}
            />
            <YAxis
              tick={{ fill: "#a3adc2", fontSize: 12 }}
              tickFormatter={(value: number) => `${numberFormatter.format(value)} MW`}
              width={96}
            />
            <Tooltip
              labelFormatter={(_, payload) => {
                if (!payload || payload.length === 0) {
                  return "";
                }
                const point = payload[0].payload as ChartPoint;
                return dateTimeFormatter.format(new Date(point.targetTimestamp)) + " UTC";
              }}
              formatter={(value, name) => {
                const numericValue =
                  typeof value === "number"
                    ? value
                    : typeof value === "string"
                      ? Number(value)
                      : Number.NaN;

                const displayValue = Number.isFinite(numericValue)
                  ? `${numberFormatter.format(numericValue)} MW`
                  : "-";

                const displayName =
                  name === "actual" || name === "Actual generation"
                    ? "Actual generation"
                    : name === "overlap" || name === "Overlap points"
                      ? "Overlap points"
                      : "Forecast generation";
                return [displayValue, displayName];
              }}
              contentStyle={{
                backgroundColor: "#0f1420",
                border: "1px solid #26324b",
                borderRadius: 12,
                color: "#e5ebfa",
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="actual"
              stroke="#60a5fa"
              strokeWidth={2}
              dot={false}
              connectNulls={false}
              name="Actual generation"
            />
            <Line
              type="monotone"
              dataKey="forecast"
              stroke="#34d399"
              strokeWidth={2.5}
              strokeDasharray="5 4"
              dot={{ r: 2 }}
              activeDot={{ r: 4 }}
              connectNulls={false}
              name="Forecast generation"
            />
            <Scatter
              dataKey="overlap"
              name="Overlap points"
              fill="#f59e0b"
              stroke="#fde68a"
              strokeWidth={1.25}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
