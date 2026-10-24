import { useEffect, useMemo, useState } from "react";
import { api, formatMw, formatStamp } from "../api/client";
import DataStatus from "../components/DataStatus";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import GenerationChart from "../components/charts/GenerationChart";

function dateOptions() {
  const days = [];
  for (let day = 1; day <= 31; day += 1) {
    days.push(`2026-01-${String(day).padStart(2, "0")}`);
  }
  return days;
}

export default function Forecasts() {
  const [deliveryDate, setDeliveryDate] = useState("2026-01-01");
  const [payload, setPayload] = useState(null);
  const [error, setError] = useState("");
  const [selectedStart, setSelectedStart] = useState("");

  useEffect(() => {
    document.title = "Forecasts | DevWindmark";
  }, []);

  useEffect(() => {
    setError("");
    setPayload(null);
    api
      .forecasts({ delivery_date: deliveryDate })
      .then((data) => {
        setPayload(data);
        const first = data.intervals.find((row) => !row.missing_actual && !row.missing_forecast);
        setSelectedStart(first?.start_time || data.intervals[0]?.start_time || "");
      })
      .catch((err) => setError(err.message));
  }, [deliveryDate]);

  const selected = useMemo(
    () => payload?.intervals.find((row) => row.start_time === selectedStart),
    [payload, selectedStart]
  );

  if (error) {
    return <ErrorState message={error} />;
  }
  if (!payload) {
    return <LoadingState label="Loading forecast explorer" />;
  }

  return (
    <section className="content">
      <header className="page-heading">
        <p className="eyebrow">Forecast explorer</p>
        <h1>Interval comparison</h1>
        <p>{payload.decision_cutoff_policy}</p>
      </header>
      <DataStatus provenance={payload.provenance} />
      <div className="toolbar">
        <label htmlFor="delivery-date">Delivery date</label>
        <select id="delivery-date" value={deliveryDate} onChange={(event) => setDeliveryDate(event.target.value)}>
          {dateOptions().map((value) => (
            <option key={value} value={value}>
              {value}
            </option>
          ))}
        </select>
        <p>
          Coverage {payload.coverage.matched_intervals}/{payload.coverage.expected_intervals} (
          {payload.coverage.coverage_percent}%). Missing actuals {payload.coverage.missing_actuals}. Missing
          forecasts {payload.coverage.missing_forecasts}.
        </p>
      </div>
      {payload.intervals.length === 0 ? (
        <div className="state-panel">No intervals for this date.</div>
      ) : (
        <>
          <GenerationChart rows={payload.intervals} />
          {selected ? (
            <article className="inspect-panel">
              <h2>Selected interval</h2>
              <p>Start: {formatStamp(selected.start_time)}</p>
              <p>Actual: {formatMw(selected.actual_generation_mw)} {selected.missing_actual ? "(missing)" : ""}</p>
              <p>Forecast: {formatMw(selected.forecast_generation_mw)} {selected.missing_forecast ? "(missing)" : ""}</p>
              <p>Error: {formatMw(selected.forecast_error_mw)}</p>
              <p>Forecast published: {formatStamp(selected.forecast_publish_time)}</p>
              <p>Decision cutoff: {formatStamp(selected.decision_cutoff)}</p>
            </article>
          ) : null}
          <div className="table-wrap">
            <table>
              <caption>Half-hourly actuals joined to the hourly forecast available at cutoff</caption>
              <thead>
                <tr>
                  <th scope="col">Start (UTC)</th>
                  <th scope="col">Actual MW</th>
                  <th scope="col">Forecast MW</th>
                  <th scope="col">Error MW</th>
                  <th scope="col">Forecast publish (UTC)</th>
                  <th scope="col">Cutoff (UTC)</th>
                  <th scope="col">Status</th>
                </tr>
              </thead>
              <tbody>
                {payload.intervals.map((row) => (
                  <tr
                    key={row.start_time}
                    className={row.start_time === selectedStart ? "selected-row" : undefined}
                    onClick={() => setSelectedStart(row.start_time)}
                    onKeyDown={(event) => {
                      if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault();
                        setSelectedStart(row.start_time);
                      }
                    }}
                    tabIndex={0}
                  >
                    <td>{row.start_time.replace("T", " ").replace("Z", "")}</td>
                    <td>{row.actual_generation_mw ?? "Missing"}</td>
                    <td>{row.forecast_generation_mw ?? "Missing"}</td>
                    <td>{row.forecast_error_mw ?? "Missing"}</td>
                    <td>{row.forecast_publish_time ? row.forecast_publish_time.replace("T", " ").replace("Z", "") : "Missing"}</td>
                    <td>{row.decision_cutoff.replace("T", " ").replace("Z", "")}</td>
                    <td>
                      {row.missing_actual || row.missing_forecast
                        ? [row.missing_actual ? "Missing actual" : null, row.missing_forecast ? "Missing forecast" : null]
                            .filter(Boolean)
                            .join("; ")
                        : "Complete"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </section>
  );
}
