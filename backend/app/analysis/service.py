from functools import lru_cache
from typing import Optional

import pandas as pd

from app.analysis.metrics import daily_accuracy, error_histogram, matched_frame, summary_metrics, time_of_day_accuracy
from app.analysis.selection import cutoff_policy_text, join_actuals_and_forecasts
from app.config import Settings, get_settings
from app.data.ingest import load_source_records
from app.data.normalize import normalize_actuals, normalize_forecasts
from app.models.schemas import (
    AccuracyResponse,
    CoverageStats,
    DailyAccuracy,
    DataProvenance,
    ForecastsResponse,
    HistogramBin,
    InsightsResponse,
    IntervalRecord,
    MethodologyResponse,
    SummaryMetrics,
    SummaryResponse,
    TimeOfDayAccuracy,
)


def _iso(value) -> Optional[str]:
    if value is None or pd.isna(value):
        return None
    if hasattr(value, "isoformat"):
        stamp = value
        if getattr(stamp, "tzinfo", None) is None:
            return stamp.isoformat() + "Z"
        return stamp.strftime("%Y-%m-%dT%H:%M:%SZ") if stamp.utcoffset().total_seconds() == 0 else stamp.isoformat()
    return str(value)


def _optional_float(value) -> Optional[float]:
    if value is None or pd.isna(value):
        return None
    return float(value)


def interval_to_record(row: pd.Series) -> IntervalRecord:
    return IntervalRecord(
        start_time=_iso(row["start_time"]),
        delivery_date=row["delivery_date"],
        settlement_period=None if pd.isna(row.get("settlement_period")) else int(row["settlement_period"]),
        actual_generation_mw=_optional_float(row.get("actual_generation_mw")),
        forecast_generation_mw=_optional_float(row.get("forecast_generation_mw")),
        forecast_publish_time=_iso(row.get("forecast_publish_time")),
        decision_cutoff=_iso(row["decision_cutoff"]),
        forecast_error_mw=_optional_float(row.get("forecast_error_mw")),
        absolute_forecast_error_mw=_optional_float(row.get("absolute_forecast_error_mw")),
        missing_actual=bool(row["missing_actual"]),
        missing_forecast=bool(row["missing_forecast"]),
    )


def provenance_from_metadata(metadata: dict, settings: Settings) -> DataProvenance:
    return DataProvenance(
        source=metadata.get("source", "demonstration"),
        labelled_as_demonstration=bool(metadata.get("labelled_as_demonstration", True)),
        actuals_dataset=metadata.get("actuals_dataset", "unknown"),
        forecasts_dataset=metadata.get("forecasts_dataset", "unknown"),
        generation_unit=settings.generation_unit,
        last_successful_refresh=metadata.get("last_successful_refresh"),
        notes=metadata.get("notes", []),
    )


@lru_cache
def load_analysis_bundle(settings_key: str = "default"):
    settings = get_settings()
    actual_records, forecast_records, metadata = load_source_records(settings)
    actuals = normalize_actuals(actual_records)
    forecasts = normalize_forecasts(forecast_records)
    intervals = join_actuals_and_forecasts(actuals, forecasts, settings)
    return settings, intervals, metadata


def filter_intervals(intervals: pd.DataFrame, delivery_date: Optional[str] = None) -> pd.DataFrame:
    if not delivery_date:
        return intervals
    return intervals.loc[intervals["delivery_date"] == delivery_date].copy()


def build_summary(delivery_date: Optional[str] = None, start_time: Optional[str] = None) -> SummaryResponse:
    settings, intervals, metadata = load_analysis_bundle()
    scoped = filter_intervals(intervals, delivery_date)
    metrics = summary_metrics(scoped)
    selected = None
    valid = matched_frame(scoped)
    if start_time:
        match = scoped.loc[scoped["start_time"] == pd.Timestamp(start_time, tz="UTC")]
        if not match.empty:
            selected = interval_to_record(match.iloc[0])
    elif not valid.empty:
        selected = interval_to_record(valid.iloc[0])
    return SummaryResponse(
        application=settings.app_name,
        analysis_period_start=settings.analysis_period_start,
        analysis_period_end=settings.analysis_period_end,
        decision_cutoff_policy=cutoff_policy_text(settings),
        generation_unit=settings.generation_unit,
        provenance=provenance_from_metadata(metadata, settings),
        metrics=SummaryMetrics(**metrics),
        selected_interval=selected,
    )


def build_forecasts(delivery_date: Optional[str] = None) -> ForecastsResponse:
    settings, intervals, metadata = load_analysis_bundle()
    scoped = filter_intervals(intervals, delivery_date)
    coverage = CoverageStats(**summary_metrics(scoped)["coverage"])
    return ForecastsResponse(
        generation_unit=settings.generation_unit,
        decision_cutoff_policy=cutoff_policy_text(settings),
        provenance=provenance_from_metadata(metadata, settings),
        coverage=coverage,
        intervals=[interval_to_record(row) for _, row in scoped.iterrows()],
    )


def build_accuracy(delivery_date: Optional[str] = None) -> AccuracyResponse:
    settings, intervals, metadata = load_analysis_bundle()
    scoped = filter_intervals(intervals, delivery_date)
    metrics = summary_metrics(scoped)
    valid = matched_frame(scoped)
    return AccuracyResponse(
        generation_unit=settings.generation_unit,
        error_convention="Forecast generation minus actual generation. Positive values are overforecasts.",
        provenance=provenance_from_metadata(metadata, settings),
        metrics=SummaryMetrics(**metrics),
        error_histogram=[HistogramBin(**item) for item in error_histogram(scoped)],
        daily=[DailyAccuracy(**item) for item in daily_accuracy(scoped)],
        time_of_day=[TimeOfDayAccuracy(**item) for item in time_of_day_accuracy(scoped)],
        scatter=[interval_to_record(row) for _, row in valid.iterrows()],
        error_series=[interval_to_record(row) for _, row in valid.iterrows()],
    )


def build_insights() -> InsightsResponse:
    settings, intervals, metadata = load_analysis_bundle()
    valid = matched_frame(intervals)
    daily = daily_accuracy(intervals)
    if valid.empty:
        observations = ["No matched forecast and actual pairs are available for this period."]
        return InsightsResponse(
            provenance=provenance_from_metadata(metadata, settings),
            observations=observations,
            limitations=_limitations(),
        )
    errors = valid["forecast_error_mw"]
    over_share = float((errors > 0).mean() * 100)
    under_share = float((errors < 0).mean() * 100)
    sorted_daily = sorted(daily, key=lambda item: (item["mae_mw"] is None, item["mae_mw"] or 0))
    mean_error = float(errors.mean())
    if mean_error > 0:
        bias_text = (
            f"Across matched January 2026 intervals, mean forecast error was {mean_error:.1f} MW. "
            "On average the selected day-ahead wind forecast was higher than outturn."
        )
    elif mean_error < 0:
        bias_text = (
            f"Across matched January 2026 intervals, mean forecast error was {mean_error:.1f} MW. "
            "On average the selected day-ahead wind forecast was lower than outturn."
        )
    else:
        bias_text = "Mean forecast error was zero on matched intervals."
    observations = [
        bias_text,
        (
            f"{over_share:.1f}% of matched intervals were overforecast and "
            f"{under_share:.1f}% were underforecast."
        ),
        (
            "When wind is underforecast, a buyer that sized day-ahead volumes on that forecast "
            "could need additional energy later. When wind is overforecast, the buyer may hold surplus. "
            "Those outcomes are directional only; required volumes also depend on demand and other generation."
        ),
        (
            "These statements describe historical forecast errors at national wind level. "
            "They are not trading advice and do not estimate imbalance cost."
        ),
    ]
    return InsightsResponse(
        provenance=provenance_from_metadata(metadata, settings),
        overforecast_share_percent=round(over_share, 2),
        underforecast_share_percent=round(under_share, 2),
        largest_overforecast_mw=round(float(errors.max()), 3),
        largest_underforecast_mw=round(float(errors.min()), 3),
        highest_mae_dates=list(reversed(sorted_daily[-3:])),
        lowest_mae_dates=sorted_daily[:3],
        observations=observations,
        limitations=_limitations(),
    )


def _limitations() -> list[str]:
    return [
        "Analysis is limited to national GB wind generation actuals (FUELHH, fuelType=WIND) and WINDFOR forecasts.",
        "FUELHH covers transmission-connected metered wind and under-represents embedded wind.",
        "Forecast errors are not imbalance volumes or procurement volumes.",
        "Demand, other fuels, interconnectors, and prices are excluded.",
        "Percentage error metrics are not used because actual generation can be low relative to capacity and would distort ratios.",
        "WINDFOR is published hourly; each hourly forecast is applied to the two half-hour FUELHH intervals in that hour.",
    ]


def build_methodology() -> MethodologyResponse:
    settings, _, metadata = load_analysis_bundle()
    return MethodologyResponse(
        application=settings.app_name,
        data_sources=[
            "Elexon Insights GET /datasets/FUELHH/stream with fuelType=WIND. generation is average MW over 30 minutes. startTime is the delivery interval start.",
            "Elexon Insights GET /datasets/WINDFOR/stream. generation is forecast MW. startTime is the hourly delivery interval start. publishTime is the forecast issue time.",
            "The public Insights REST API does not require an API key. HTTP 429 is retried.",
        ],
        forecast_selection_policy=[
            "For each delivery interval, keep WINDFOR records whose publishTime is at or before the configured decision cutoff.",
            "Among remaining records for the same hourly startTime, keep the latest publishTime.",
            "Duplicate publishTime and startTime pairs keep the record with the highest generation after a deterministic sort.",
            "Forecasts issued after the cutoff are never used, including later intra-day revisions.",
        ],
        decision_cutoff={
            "timezone": settings.decision_timezone,
            "clock_time": settings.decision_cutoff_time,
            "offset_days": settings.decision_offset_days,
            "policy": cutoff_policy_text(settings),
            "basis": (
                "Default 09:20 Europe/London on D-1 follows the EPEX SPOT GB 60-minute day-ahead "
                "auction order-book close. This is a configurable procurement-timing assumption, "
                "not a claim that every GB utility must trade that auction. Nord Pool N2EX GB "
                "day-ahead gate is later (09:50 GMT/BST). A utility may freeze bids earlier."
            ),
            "assumption": True,
        },
        timestamp_handling=[
            "Elexon timestamps are parsed as UTC.",
            "Delivery dates and cutoffs are computed in Europe/London so GMT/BST transitions are respected.",
            "January 2026 is entirely GMT (UTC+0), so London local time equals UTC for this study window.",
            "Half-hourly actuals are joined to the hourly WINDFOR interval by flooring startTime to the hour in UTC.",
        ],
        metric_definitions={
            "forecast_error": "forecast_generation_mw - actual_generation_mw",
            "positive_error": "wind was overforecast",
            "negative_error": "wind was underforecast",
            "mae": "mean of absolute forecast error on matched intervals, MW",
            "rmse": "square root of mean squared forecast error on matched intervals, MW",
            "bias": "mean forecast error on matched intervals, MW",
            "coverage": "matched intervals divided by expected January 2026 half-hour intervals",
            "units": settings.generation_unit,
        },
        missing_data=[
            "Expected grid is every 30 minutes from 2026-01-01 00:00 UTC through 2026-01-31 23:30 UTC.",
            "An interval is unmatched if the actual or the eligible forecast is missing.",
            "Unmatched intervals are excluded from MAE, RMSE, and bias and are counted in coverage.",
        ],
        limitations=_limitations(),
        reproducibility=[
            "python -m app.cli refresh downloads FUELHH and WINDFOR into backend/data/cache.",
            "Cached JSON is reused on subsequent starts to avoid repeated API calls.",
            "If the API is unavailable and no cache exists, a labelled demonstration dataset is used.",
            "Cutoff time, timezone, and analysis period are environment variables.",
        ],
        provenance=provenance_from_metadata(metadata, settings),
    )


def refresh_and_clear() -> dict:
    from app.data.ingest import refresh_from_elexon

    load_analysis_bundle.cache_clear()
    return refresh_from_elexon(get_settings())
