import type { ForecastResponse } from "@/lib/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

type ForecastQuery = {
  start: string;
  end: string;
  horizon: number;
};

function assertOkResponse(response: Response, payload: unknown): void {
  if (response.ok) {
    return;
  }

  if (
    payload &&
    typeof payload === "object" &&
    "detail" in payload &&
    typeof (payload as { detail?: unknown }).detail === "string"
  ) {
    throw new Error((payload as { detail: string }).detail);
  }

  throw new Error(`API request failed with status ${response.status}.`);
}

export async function fetchForecasts(query: ForecastQuery): Promise<ForecastResponse> {
  const search = new URLSearchParams({
    start: query.start,
    end: query.end,
    horizon: String(query.horizon),
  });

  const response = await fetch(`${API_BASE_URL}/api/forecasts?${search.toString()}`, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
    cache: "no-store",
  });

  const payload: unknown = await response.json();
  assertOkResponse(response, payload);

  return payload as ForecastResponse;
}
