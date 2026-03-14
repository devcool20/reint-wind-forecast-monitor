export type ForecastPoint = {
  target_time: string;
  actual_generation_mw: number | null;
  forecast_generation_mw: number | null;
  selected_publish_time: string | null;
  selected_horizon_hours: number | null;
};

export type ForecastMetadata = {
  points_total: number;
  points_with_actual: number;
  points_with_forecast: number;
  points_with_both: number;
};

export type ForecastResponse = {
  start_time: string;
  end_time: string;
  forecast_horizon_hours: number;
  points: ForecastPoint[];
  metadata: ForecastMetadata;
};
