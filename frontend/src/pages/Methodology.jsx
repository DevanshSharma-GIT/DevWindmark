import { useEffect, useState } from "react";
import { api } from "../api/client";
import DataStatus from "../components/DataStatus";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";

export default function Methodology() {
  const [payload, setPayload] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    document.title = "Methodology | DevWindmark";
    api.methodology().then(setPayload).catch((err) => setError(err.message));
  }, []);

  if (error) {
    return <ErrorState message={error} />;
  }
  if (!payload) {
    return <LoadingState label="Loading methodology" />;
  }

  const cutoff = payload.decision_cutoff;
  const metrics = payload.metric_definitions;

  return (
    <section className="content">
      <header className="page-heading">
        <p className="eyebrow">Methodology</p>
        <h1>How DevWindmark selects and scores forecasts</h1>
      </header>
      <DataStatus provenance={payload.provenance} />
      <article className="copy-block">
        <h2>Elexon data sources</h2>
        {payload.data_sources.map((item) => (
          <p key={item}>{item}</p>
        ))}
        <h2>Forecast selection policy</h2>
        <ul>
          {payload.forecast_selection_policy.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
        <h2>Decision cutoff</h2>
        <p>{cutoff.policy}</p>
        <p>
          Clock: {cutoff.clock_time} {cutoff.timezone}, {cutoff.offset_days} day before delivery. This is an
          assumption: {cutoff.basis}
        </p>
        <h2>Timestamps and time zones</h2>
        <ul>
          {payload.timestamp_handling.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
        <h2>Metric definitions</h2>
        <ul>
          <li>Forecast error: {metrics.forecast_error}. {metrics.positive_error}. {metrics.negative_error}.</li>
          <li>MAE: {metrics.mae}</li>
          <li>RMSE: {metrics.rmse}</li>
          <li>Bias: {metrics.bias}</li>
          <li>Coverage: {metrics.coverage}</li>
          <li>Units: {metrics.units}</li>
        </ul>
        <h2>Missing data and exclusions</h2>
        <ul>
          {payload.missing_data.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
        <h2>Limitations</h2>
        <ul>
          {payload.limitations.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
        <h2>Reproducibility</h2>
        <ul>
          {payload.reproducibility.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </article>
    </section>
  );
}
