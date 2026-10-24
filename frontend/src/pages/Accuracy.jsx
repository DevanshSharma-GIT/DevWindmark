import { useEffect, useState } from "react";
import { api, formatMw, formatPercent } from "../api/client";
import DataStatus from "../components/DataStatus";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import MetricCard from "../components/MetricCard";
import DailyAccuracyChart from "../components/charts/DailyAccuracyChart";
import ErrorDistributionChart from "../components/charts/ErrorDistributionChart";
import ErrorTimeChart from "../components/charts/ErrorTimeChart";
import HourlyAccuracyChart from "../components/charts/HourlyAccuracyChart";
import ScatterCompareChart from "../components/charts/ScatterCompareChart";

export default function Accuracy() {
  const [accuracy, setAccuracy] = useState(null);
  const [insights, setInsights] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    document.title = "Accuracy | DevWindmark";
    Promise.all([api.accuracy(), api.insights()])
      .then(([accuracyPayload, insightsPayload]) => {
        setAccuracy(accuracyPayload);
        setInsights(insightsPayload);
      })
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return <ErrorState message={error} />;
  }
  if (!accuracy || !insights) {
    return <LoadingState label="Loading accuracy analysis" />;
  }

  return (
    <section className="content">
      <header className="page-heading">
        <p className="eyebrow">Forecast accuracy</p>
        <h1>Error, coverage, and time structure</h1>
        <p>{accuracy.error_convention} All figures are MW unless noted. Percentage error is not reported because low actual generation would distort the ratio.</p>
      </header>
      <DataStatus provenance={accuracy.provenance} />
      <div className="metric-grid">
        <MetricCard label="MAE" value={formatMw(accuracy.metrics.mae_mw)} />
        <MetricCard label="RMSE" value={formatMw(accuracy.metrics.rmse_mw)} />
        <MetricCard label="Bias" value={formatMw(accuracy.metrics.mean_forecast_error_mw)} />
        <MetricCard label="Coverage" value={formatPercent(accuracy.metrics.coverage.coverage_percent)} hint={`${accuracy.metrics.coverage.matched_intervals} matched intervals`} />
      </div>
      <div className="chart-grid">
        <section>
          <h2>Error distribution</h2>
          <ErrorDistributionChart bins={accuracy.error_histogram} />
        </section>
        <section>
          <h2>Forecast versus actual</h2>
          <ScatterCompareChart rows={accuracy.scatter} />
        </section>
        <section className="wide">
          <h2>Error over time</h2>
          <ErrorTimeChart rows={accuracy.error_series} />
        </section>
        <section>
          <h2>Daily MAE</h2>
          <DailyAccuracyChart rows={accuracy.daily} />
        </section>
        <section>
          <h2>Time-of-day MAE (UTC hour of interval start)</h2>
          <HourlyAccuracyChart rows={accuracy.time_of_day} />
        </section>
      </div>
      <section className="copy-block">
        <h2>What the results mean</h2>
        <p>
          MAE describes typical absolute miss size. RMSE penalises large misses more heavily. Bias shows
          whether the selected cutoff forecast tended to sit above or below outturn.
        </p>
        {insights.observations.map((item) => (
          <p key={item}>{item}</p>
        ))}
        <h2>Limitations</h2>
        {insights.limitations.map((item) => (
          <p key={item}>{item}</p>
        ))}
      </section>
    </section>
  );
}
