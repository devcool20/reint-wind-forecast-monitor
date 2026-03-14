export function LoadingSpinner() {
  return (
    <div className="loading-wrap" role="status" aria-live="polite">
      <div className="loading-spinner" />
      <p>Loading forecast data...</p>
    </div>
  );
}
