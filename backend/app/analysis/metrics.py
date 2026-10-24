from typing import Optional

import numpy as np
import pandas as pd


def matched_frame(intervals: pd.DataFrame) -> pd.DataFrame:
    if intervals.empty:
        return intervals
    return intervals.loc[~intervals["missing_actual"] & ~intervals["missing_forecast"]].copy()


def coverage_stats(intervals: pd.DataFrame) -> dict:
    expected = int(len(intervals))
    matched = int((~intervals["missing_actual"] & ~intervals["missing_forecast"]).sum()) if expected else 0
    missing_actuals = int(intervals["missing_actual"].sum()) if expected else 0
    missing_forecasts = int(intervals["missing_forecast"].sum()) if expected else 0
    coverage_percent = round((matched / expected) * 100, 2) if expected else 0.0
    return {
        "expected_intervals": expected,
        "matched_intervals": matched,
        "missing_actuals": missing_actuals,
        "missing_forecasts": missing_forecasts,
        "coverage_percent": coverage_percent,
    }


def _metric(values: np.ndarray, reducer) -> Optional[float]:
    if values.size == 0:
        return None
    result = reducer(values)
    if result is None or np.isnan(result):
        return None
    return float(round(result, 3))


def summary_metrics(intervals: pd.DataFrame) -> dict:
    coverage = coverage_stats(intervals)
    valid = matched_frame(intervals)
    errors = valid["forecast_error_mw"].to_numpy(dtype=float) if not valid.empty else np.array([])
    actuals = valid["actual_generation_mw"].to_numpy(dtype=float) if not valid.empty else np.array([])
    forecasts = valid["forecast_generation_mw"].to_numpy(dtype=float) if not valid.empty else np.array([])
    return {
        "mae_mw": _metric(np.abs(errors), np.mean),
        "rmse_mw": _metric(errors, lambda values: float(np.sqrt(np.mean(np.square(values))))),
        "mean_forecast_error_mw": _metric(errors, np.mean),
        "mean_actual_mw": _metric(actuals, np.mean),
        "mean_forecast_mw": _metric(forecasts, np.mean),
        "matched_intervals": coverage["matched_intervals"],
        "coverage": coverage,
    }


def error_histogram(intervals: pd.DataFrame, bin_width: float = 500.0) -> list[dict]:
    valid = matched_frame(intervals)
    if valid.empty:
        return []
    errors = valid["forecast_error_mw"].to_numpy(dtype=float)
    lower = np.floor(errors.min() / bin_width) * bin_width
    upper = np.ceil(errors.max() / bin_width) * bin_width
    if lower == upper:
        upper = lower + bin_width
    edges = np.arange(lower, upper + bin_width, bin_width)
    counts, edges = np.histogram(errors, bins=edges)
    return [
        {
            "bin_start_mw": float(edges[index]),
            "bin_end_mw": float(edges[index + 1]),
            "count": int(counts[index]),
        }
        for index in range(len(counts))
    ]


def daily_accuracy(intervals: pd.DataFrame) -> list[dict]:
    valid = matched_frame(intervals)
    if valid.empty:
        return []
    grouped = valid.groupby("delivery_date", sort=True)
    rows = []
    for delivery_date, group in grouped:
        errors = group["forecast_error_mw"].to_numpy(dtype=float)
        rows.append(
            {
                "delivery_date": delivery_date,
                "matched_intervals": int(len(group)),
                "mae_mw": _metric(np.abs(errors), np.mean),
                "rmse_mw": _metric(errors, lambda values: float(np.sqrt(np.mean(np.square(values))))),
                "mean_forecast_error_mw": _metric(errors, np.mean),
                "mean_actual_mw": _metric(group["actual_generation_mw"].to_numpy(dtype=float), np.mean),
                "mean_forecast_mw": _metric(group["forecast_generation_mw"].to_numpy(dtype=float), np.mean),
            }
        )
    return rows


def time_of_day_accuracy(intervals: pd.DataFrame) -> list[dict]:
    valid = matched_frame(intervals)
    if valid.empty:
        return []
    working = valid.copy()
    working["hour_ending_utc"] = working["start_time"].dt.hour
    rows = []
    for hour, group in working.groupby("hour_ending_utc", sort=True):
        errors = group["forecast_error_mw"].to_numpy(dtype=float)
        rows.append(
            {
                "hour_ending_utc": int(hour),
                "matched_intervals": int(len(group)),
                "mae_mw": _metric(np.abs(errors), np.mean),
                "rmse_mw": _metric(errors, lambda values: float(np.sqrt(np.mean(np.square(values))))),
                "mean_forecast_error_mw": _metric(errors, np.mean),
            }
        )
    return rows
