import { formatStamp } from "../api/client";

export default function DataStatus({ provenance }) {
  if (!provenance) {
    return null;
  }
  const demonstration = provenance.labelled_as_demonstration || provenance.source === "demonstration";
  return (
    <aside className={demonstration ? "data-status warning" : "data-status"} aria-live="polite">
      <p>
        <strong>{demonstration ? "Demonstration data" : "Elexon Insights data"}</strong>
      </p>
      <p>
        Actuals: {provenance.actuals_dataset}. Forecasts: {provenance.forecasts_dataset}. Units:{" "}
        {provenance.generation_unit}.
      </p>
      <p>Last successful refresh: {formatStamp(provenance.last_successful_refresh)}</p>
      {demonstration ? (
        <p>Synthetic values are labelled demonstration data and are not official Elexon observations.</p>
      ) : null}
    </aside>
  );
}
