"use client";

import {
  LineChart,
  CartesianGrid,
  Line,
  ResponsiveContainer,
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

function formatCompact(value: number): string {
  if (Math.abs(value) >= 1000) {
    return `${(value / 1000).toFixed(value % 1000 === 0 ? 0 : 1)}k`;
  }
  return String(value);
}

function buildChartData(points: ForecastPoint[]): ChartPoint[] {
  return points.map((point) => ({
    targetTimeLabel: dateTimeFormatter.format(new Date(point.target_time)),
    targetTimestamp: point.target_time,
    actual: point.actual_generation_mw,
    forecast: point.forecast_generation_mw,
  }));
}

export function ForecastChart({ points, appliedHorizonHours }: ForecastChartProps) {
  const data = buildChartData(points);
  const forecastPointCount = data.filter((point) => point.forecast !== null).length;
  const actualPointCount = data.filter((point) => point.actual !== null).length;

  if (data.length === 0) {
    return (
      <section className="panel chart-panel">
        <h2 className="panel-title">Wind Generation Series</h2>
        <p className="muted">No points returned for this date range and horizon.</p>
      </section>
    );
  }

  return (
    <section className="chart-panel-light">
      <h2 className="chart-title-light">Wind Generation Series</h2>
      <p className="chart-subtitle-light">
        Applied horizon: {appliedHorizonHours ?? "-"}h &middot; Actual points: {actualPointCount} &middot; Forecast
        points: {forecastPointCount}
      </p>
      <div className="chart-wrap">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 16, right: 24, left: 8, bottom: 24 }}>
            <CartesianGrid stroke="#e5e7eb" strokeDasharray="none" vertical={false} />
            <XAxis
              dataKey="targetTimeLabel"
              minTickGap={36}
              tick={{ fill: "#6b7280", fontSize: 12 }}
              tickMargin={10}
              axisLine={{ stroke: "#d1d5db" }}
              tickLine={{ stroke: "#d1d5db" }}
              label={{
                value: "Target Time End (UTC)",
                position: "insideBottom",
                offset: -16,
                style: { fill: "#6b7280", fontSize: 13, fontWeight: 500 },
              }}
            />
            <YAxis
              tick={{ fill: "#6b7280", fontSize: 12 }}
              tickFormatter={formatCompact}
              width={56}
              axisLine={{ stroke: "#d1d5db" }}
              tickLine={{ stroke: "#d1d5db" }}
              label={{
                value: "Power (MW)",
                angle: -90,
                position: "insideLeft",
                offset: 4,
                style: { fill: "#6b7280", fontSize: 13, fontWeight: 500, textAnchor: "middle" },
              }}
            />
            <Tooltip
              labelFormatter={(_, payload) => {
                if (!payload || payload.length === 0) return "";
                const point = payload[0].payload as ChartPoint;
                return dateTimeFormatter.format(new Date(point.targetTimestamp)) + " UTC";
              }}
              formatter={(value, name) => {
                const numericValue =
                  typeof value === "number" ? value : typeof value === "string" ? Number(value) : Number.NaN;
                const displayValue = Number.isFinite(numericValue)
                  ? `${numberFormatter.format(numericValue)} MW`
                  : "-";
                const displayName = name === "actual" ? "Actual" : "Forecast";
                return [displayValue, displayName];
              }}
              contentStyle={{
                backgroundColor: "#ffffff",
                border: "1px solid #e5e7eb",
                borderRadius: 8,
                color: "#1f2937",
                boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
              }}
              cursor={{ stroke: "#9ca3af", strokeDasharray: "4 4" }}
            />
            <Line
              type="monotone"
              dataKey="actual"
              stroke="#3b82f6"
              strokeWidth={2.5}
              dot={false}
              activeDot={{ r: 4, fill: "#3b82f6", stroke: "#fff", strokeWidth: 2 }}
              connectNulls={false}
              name="actual"
            />
            <Line
              type="monotone"
              dataKey="forecast"
              stroke="#22c55e"
              strokeWidth={2.5}
              dot={false}
              activeDot={{ r: 4, fill: "#22c55e", stroke: "#fff", strokeWidth: 2 }}
              connectNulls
              name="forecast"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
