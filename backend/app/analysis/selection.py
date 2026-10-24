from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import pandas as pd

from app.config import Settings


def parse_cutoff_clock(value: str) -> time:
    hour_text, minute_text = value.split(":")
    return time(hour=int(hour_text), minute=int(minute_text))


def decision_cutoff_for_interval(start_time: datetime, settings: Settings) -> datetime:
    zone = ZoneInfo(settings.decision_timezone)
    local_start = start_time.astimezone(zone)
    decision_date = local_start.date() - timedelta(days=settings.decision_offset_days)
    cutoff_clock = parse_cutoff_clock(settings.decision_cutoff_time)
    local_cutoff = datetime.combine(decision_date, cutoff_clock, tzinfo=zone)
    return local_cutoff.astimezone(timezone.utc)


def cutoff_policy_text(settings: Settings) -> str:
    return (
        f"Latest WINDFOR record with publishTime at or before "
        f"{settings.decision_cutoff_time} {settings.decision_timezone} "
        f"on the calendar day {settings.decision_offset_days} day(s) before "
        "the Europe/London delivery date of the interval."
    )


def expected_half_hours(period_start: str, period_end: str) -> pd.DatetimeIndex:
    start = pd.Timestamp(period_start, tz="UTC")
    end = pd.Timestamp(period_end, tz="UTC") + pd.Timedelta(days=1) - pd.Timedelta(minutes=30)
    return pd.date_range(start=start, end=end, freq="30min", tz="UTC")


def select_latest_eligible_forecasts(forecasts: pd.DataFrame, settings: Settings) -> pd.DataFrame:
    if forecasts.empty:
        return forecasts.copy()
    working = forecasts.copy()
    working["start_time"] = pd.to_datetime(working["start_time"], utc=True)
    working["publish_time"] = pd.to_datetime(working["publish_time"], utc=True)
    working["decision_cutoff"] = working["start_time"].map(
        lambda stamp: decision_cutoff_for_interval(stamp.to_pydatetime(), settings)
    )
    working["decision_cutoff"] = pd.to_datetime(working["decision_cutoff"], utc=True)
    eligible = working.loc[working["publish_time"] <= working["decision_cutoff"]].copy()
    if eligible.empty:
        return eligible
    eligible = eligible.sort_values(["start_time", "publish_time", "forecast_generation_mw"])
    selected = eligible.drop_duplicates(subset=["start_time"], keep="last")
    return selected.reset_index(drop=True)


def align_forecasts_to_half_hours(selected_hourly: pd.DataFrame, half_hours: pd.DatetimeIndex) -> pd.DataFrame:
    grid = pd.DataFrame({"start_time": half_hours})
    if selected_hourly.empty:
        grid["forecast_generation_mw"] = pd.NA
        grid["forecast_publish_time"] = pd.NaT
        grid["decision_cutoff"] = pd.NaT
        grid["forecast_hour_start"] = grid["start_time"].dt.floor("h")
        return grid
    hourly = selected_hourly.copy()
    hourly["forecast_hour_start"] = pd.to_datetime(hourly["start_time"], utc=True).dt.floor("h")
    hourly = hourly.rename(
        columns={
            "publish_time": "forecast_publish_time",
            "start_time": "forecast_interval_start",
        }
    )
    grid["forecast_hour_start"] = grid["start_time"].dt.floor("h")
    merged = grid.merge(
        hourly[
            [
                "forecast_hour_start",
                "forecast_generation_mw",
                "forecast_publish_time",
                "decision_cutoff",
            ]
        ],
        on="forecast_hour_start",
        how="left",
    )
    return merged


def join_actuals_and_forecasts(
    actuals: pd.DataFrame,
    forecasts: pd.DataFrame,
    settings: Settings,
) -> pd.DataFrame:
    period_index = expected_half_hours(settings.analysis_period_start, settings.analysis_period_end)
    selected = select_latest_eligible_forecasts(forecasts, settings)
    aligned = align_forecasts_to_half_hours(selected, period_index)
    actual_frame = actuals.copy()
    if not actual_frame.empty:
        actual_frame["start_time"] = pd.to_datetime(actual_frame["start_time"], utc=True)
        actual_frame = actual_frame[
            [
                "start_time",
                "actual_generation_mw",
                "settlement_period",
                "settlement_date",
            ]
        ]
    else:
        actual_frame = pd.DataFrame(
            columns=["start_time", "actual_generation_mw", "settlement_period", "settlement_date"]
        )
    combined = aligned.merge(actual_frame, on="start_time", how="left")
    zone = ZoneInfo(settings.decision_timezone)
    combined["delivery_date"] = combined["start_time"].map(lambda stamp: stamp.astimezone(zone).date().isoformat())
    missing_cutoff = combined["decision_cutoff"].isna()
    combined.loc[missing_cutoff, "decision_cutoff"] = combined.loc[missing_cutoff, "start_time"].map(
        lambda stamp: decision_cutoff_for_interval(stamp.to_pydatetime(), settings)
    )
    combined["missing_actual"] = combined["actual_generation_mw"].isna()
    combined["missing_forecast"] = combined["forecast_generation_mw"].isna()
    combined["forecast_error_mw"] = combined["forecast_generation_mw"] - combined["actual_generation_mw"]
    combined["absolute_forecast_error_mw"] = combined["forecast_error_mw"].abs()
    return combined.sort_values("start_time").reset_index(drop=True)
