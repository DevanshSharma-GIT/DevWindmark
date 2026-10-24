import pandas as pd
import pytest

from app.config import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(
        analysis_period_start="2026-01-01",
        analysis_period_end="2026-01-02",
        decision_timezone="Europe/London",
        decision_cutoff_time="09:20",
        decision_offset_days=1,
        generation_unit="MW",
    )


@pytest.fixture
def actuals_frame() -> pd.DataFrame:
    stamps = pd.date_range("2026-01-01T00:00:00Z", periods=4, freq="30min", tz="UTC")
    return pd.DataFrame(
        {
            "start_time": stamps,
            "publish_time": stamps + pd.Timedelta(minutes=30),
            "settlement_date": ["2026-01-01"] * 4,
            "settlement_period": [1, 2, 3, 4],
            "actual_generation_mw": [1000.0, 1100.0, 1200.0, 900.0],
        }
    )


@pytest.fixture
def forecasts_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "start_time": pd.to_datetime(
                [
                    "2026-01-01T00:00:00Z",
                    "2026-01-01T00:00:00Z",
                    "2026-01-01T00:00:00Z",
                    "2026-01-01T01:00:00Z",
                    "2026-01-01T01:00:00Z",
                    "2026-01-01T02:00:00Z",
                ],
                utc=True,
            ),
            "publish_time": pd.to_datetime(
                [
                    "2025-12-31T07:30:00Z",
                    "2025-12-31T09:30:00Z",
                    "2025-12-31T07:30:00Z",
                    "2025-12-31T07:30:00Z",
                    "2025-12-30T07:30:00Z",
                    "2025-12-31T07:30:00Z",
                ],
                utc=True,
            ),
            "forecast_generation_mw": [1500.0, 9999.0, 1400.0, 1300.0, 800.0, 1250.0],
        }
    )
