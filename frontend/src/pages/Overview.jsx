import { useEffect, useState } from "react";
import { api, formatMw, formatPercent, formatStamp } from "../api/client";
import DataStatus from "../components/DataStatus";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import MetricCard from "../components/MetricCard";

export default function Overview() {
  const [summary, setSummary] = useState(null);
  const [insights, setInsights] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    document.title = "Overview | DevWindmark";
    Promise.all([api.summary(), api.insights()])
      .then(([summaryPayload, insightsPayload]) => {
        setSummary(summaryPayload);
        setInsights(insightsPayload);
      })
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return <ErrorState message={error} />;
  }
  if (!summary || !insights) {
    return <LoadingState label="Loading executive dashboard" />;
  }

  const selected = summary.selected_interval;
  const metrics = summary.metrics;

  return (
    <section className="content">
      <header className="page-heading">
        <p className="eyebrow">Executive dashboard</p>
        <h1>January 2026 wind forecast position</h1>
        <p>
          Metrics use only WINDFOR publications at or before {summary.decision_cutoff_policy}. Forecast
          error equals forecast minus actual. Positive error is an overforecast.
        </p>
      </header>
      <DataStatus provenance={summary.provenance} />
      <div className="metric-grid">
        <MetricCard label="Selected interval actual" value={formatMw(selected?.actual_generation_mw)} hint={selected ? formatStamp(selected.start_time) : "No matched interval"} />
        <MetricCard label="Selected interval forecast" value={formatMw(selected?.forecast_generation_mw)} hint={selected ? `Published ${formatStamp(selected.forecast_publish_time)}` : "No matched interval"} />
        <MetricCard label="Selected interval error" value={formatMw(selected?.forecast_error_mw)} hint="Forecast minus actual" />
        <MetricCard label="MAE" value={formatMw(metrics.mae_mw)} hint="Mean absolute error on matched intervals" />
        <MetricCard label="RMSE" value={formatMw(metrics.rmse_mw)} hint="Root mean squared error on matched intervals" />
        <MetricCard label="Mean forecast bias" value={formatMw(metrics.mean_forecast_error_mw)} hint="Mean forecast error" />
        <MetricCard
          label="Forecast coverage"
          value={formatPercent(metrics.coverage.coverage_percent)}
          hint={`${metrics.coverage.matched_intervals} of ${metrics.coverage.expected_intervals} half-hour intervals`}
        />
        <MetricCard label="Last refresh" value={summary.provenance.last_successful_refresh ? formatStamp(summary.provenance.last_successful_refresh) : "Not recorded"} />
      </div>
      <section className="copy-block">
        <h2>Procurement context</h2>
        {insights.observations.map((item) => (
          <p key={item}>{item}</p>
        ))}
        <h3>Historical extremes in this sample</h3>
        <p>
          Largest overforecast: {formatMw(insights.largest_overforecast_mw)}. Largest underforecast:{" "}
          {formatMw(insights.largest_underforecast_mw)}.
        </p>
        <p className="fine-print">{insights.limitations[2]}</p>
      </section>
    </section>
  );
}
