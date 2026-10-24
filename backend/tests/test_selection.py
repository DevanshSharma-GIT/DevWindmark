from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pandas as pd

from app.analysis.selection import (
    decision_cutoff_for_interval,
    join_actuals_and_forecasts,
    select_latest_eligible_forecasts,
)
from app.data.normalize import normalize_actuals, normalize_forecasts


def test_cutoff_uses_london_previous_day(settings):
    start = datetime(2026, 1, 1, 15, 30, tzinfo=timezone.utc)
    cutoff = decision_cutoff_for_interval(start, settings)
    expected = datetime(2025, 12, 31, 9, 20, tzinfo=ZoneInfo("Europe/London")).astimezone(timezone.utc)
    assert cutoff == expected


def test_excludes_forecasts_after_cutoff(settings, forecasts_frame):
    selected = select_latest_eligible_forecasts(forecasts_frame, settings)
    hour_zero = selected.loc[selected["start_time"] == pd.Timestamp("2026-01-01T00:00:00Z")]
    assert len(hour_zero) == 1
    assert hour_zero.iloc[0]["forecast_generation_mw"] == 1500.0
    assert hour_zero.iloc[0]["publish_time"] == pd.Timestamp("2025-12-31T07:30:00Z")
    assert 9999.0 not in set(selected["forecast_generation_mw"])


def test_latest_eligible_publish_time_wins(settings, forecasts_frame):
    selected = select_latest_eligible_forecasts(forecasts_frame, settings)
    hour_one = selected.loc[selected["start_time"] == pd.Timestamp("2026-01-01T01:00:00Z")].iloc[0]
    assert hour_one["forecast_generation_mw"] == 1300.0
    assert hour_one["publish_time"] == pd.Timestamp("2025-12-31T07:30:00Z")


def test_duplicate_records_are_deterministic():
    records = [
        {
            "dataset": "WINDFOR",
            "publishTime": "2025-12-31T07:30:00Z",
            "startTime": "2026-01-01T00:00:00Z",
            "generation": 10,
        },
        {
            "dataset": "WINDFOR",
            "publishTime": "2025-12-31T07:30:00Z",
            "startTime": "2026-01-01T00:00:00Z",
            "generation": 20,
        },
    ]
    normalized = normalize_forecasts(records)
    assert len(normalized) == 1
    assert normalized.iloc[0]["forecast_generation_mw"] == 20.0


def test_duplicate_actuals_keep_latest_publish():
    records = [
        {
            "dataset": "FUELHH",
            "fuelType": "WIND",
            "publishTime": "2026-01-01T00:30:00Z",
            "startTime": "2026-01-01T00:00:00Z",
            "settlementDate": "2026-01-01",
            "settlementPeriod": 1,
            "generation": 100,
        },
        {
            "dataset": "FUELHH",
            "fuelType": "WIND",
            "publishTime": "2026-01-01T01:00:00Z",
            "startTime": "2026-01-01T00:00:00Z",
            "settlementDate": "2026-01-01",
            "settlementPeriod": 1,
            "generation": 111,
        },
    ]
    normalized = normalize_actuals(records)
    assert len(normalized) == 1
    assert normalized.iloc[0]["actual_generation_mw"] == 111.0


def test_join_matches_half_hours_to_hourly_forecast(settings, actuals_frame, forecasts_frame):
    combined = join_actuals_and_forecasts(actuals_frame, forecasts_frame, settings)
    first_hour = combined.loc[combined["start_time"] < pd.Timestamp("2026-01-01T01:00:00Z")]
    assert set(first_hour["forecast_generation_mw"]) == {1500.0}
    second_hour = combined.loc[
        (combined["start_time"] >= pd.Timestamp("2026-01-01T01:00:00Z"))
        & (combined["start_time"] < pd.Timestamp("2026-01-01T02:00:00Z"))
    ]
    assert set(second_hour["forecast_generation_mw"].dropna()) == {1300.0}


def test_missing_forecast_and_actual_flags(settings, actuals_frame, forecasts_frame):
    combined = join_actuals_and_forecasts(actuals_frame, forecasts_frame, settings)
    later = combined.loc[combined["start_time"] >= pd.Timestamp("2026-01-01T02:00:00Z")]
    assert later["missing_actual"].all()
    jan2_morning = combined.loc[combined["delivery_date"] == "2026-01-02"]
    assert jan2_morning["missing_forecast"].all()


def test_malformed_records_are_dropped():
    actuals = normalize_actuals(
        [
            {"fuelType": "WIND", "startTime": "not-a-date", "generation": 10},
            {"fuelType": "CCGT", "startTime": "2026-01-01T00:00:00Z", "generation": 10},
            {"fuelType": "WIND", "startTime": "2026-01-01T00:00:00Z", "generation": "mw"},
            {
                "fuelType": "WIND",
                "startTime": "2026-01-01T00:00:00Z",
                "generation": 50,
                "publishTime": "2026-01-01T00:30:00Z",
            },
        ]
    )
    assert len(actuals) == 1
    assert actuals.iloc[0]["actual_generation_mw"] == 50.0
