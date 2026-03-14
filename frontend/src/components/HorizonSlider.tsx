"use client";

type HorizonSliderProps = {
  horizon: number;
  onHorizonChange: (value: number) => void;
  min?: number;
  max?: number;
};

export function HorizonSlider({
  horizon,
  onHorizonChange,
  min = 0,
  max = 48,
}: HorizonSliderProps) {
  return (
    <section className="panel">
      <div className="slider-row">
        <h2 className="panel-title">Forecast Horizon</h2>
        <span className="badge">{horizon}h</span>
      </div>
      <input
        aria-label="Forecast horizon in hours"
        className="slider"
        type="range"
        min={min}
        max={max}
        step={1}
        value={horizon}
        onChange={(event) => onHorizonChange(Number(event.target.value))}
        onInput={(event) => onHorizonChange(Number((event.target as HTMLInputElement).value))}
      />
      <div className="slider-caption">
        <span>{min}h</span>
        <span>{max}h</span>
      </div>
    </section>
  );
}
