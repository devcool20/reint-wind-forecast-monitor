"use client";

type DateRangePickerProps = {
  startDate: string;
  endDate: string;
  onStartDateChange: (value: string) => void;
  onEndDateChange: (value: string) => void;
  minDate: string;
  maxDate: string;
};

export function DateRangePicker({
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
  minDate,
  maxDate,
}: DateRangePickerProps) {
  return (
    <section className="panel">
      <h2 className="panel-title">Date Range</h2>
      <div className="control-grid">
        <label className="input-label" htmlFor="start-date">
          Start date
        </label>
        <input
          id="start-date"
          className="input"
          type="date"
          value={startDate}
          min={minDate}
          max={endDate || maxDate}
          onChange={(event) => onStartDateChange(event.target.value)}
        />
        <label className="input-label" htmlFor="end-date">
          End date
        </label>
        <input
          id="end-date"
          className="input"
          type="date"
          value={endDate}
          min={startDate || minDate}
          max={maxDate}
          onChange={(event) => onEndDateChange(event.target.value)}
        />
      </div>
    </section>
  );
}
