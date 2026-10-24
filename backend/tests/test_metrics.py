import pandas as pd

from app.analysis.metrics import daily_accuracy, error_histogram, summary_metrics
from app.analysis.selection import join_actuals_and_forecasts


def test_mae_rmse_bias_and_units(settings, actuals_frame, forecasts_frame):
    combined = join_actuals_and_forecasts(actuals_frame, forecasts_frame, settings)
    matched = combined.loc[~combined["missing_actual"] & ~combined["missing_forecast"]]
    metrics = summary_metrics(combined)
    errors = matched["forecast_generation_mw"] - matched["actual_generation_mw"]
    mae = float(errors.abs().mean())
    rmse = float((errors.pow(2).mean()) ** 0.5)
    bias = float(errors.mean())
    assert metrics["mae_mw"] == round(mae, 3)
    assert metrics["rmse_mw"] == round(rmse, 3)
    assert metrics["mean_forecast_error_mw"] == round(bias, 3)
    assert settings.generation_unit == "MW"
    assert metrics["coverage"]["matched_intervals"] == 4


def test_date_filter_changes_metrics(settings, actuals_frame, forecasts_frame):
    combined = join_actuals_and_forecasts(actuals_frame, forecasts_frame, settings)
    jan1 = combined.loc[combined["delivery_date"] == "2026-01-01"]
    jan2 = combined.loc[combined["delivery_date"] == "2026-01-02"]
    assert summary_metrics(jan1)["matched_intervals"] == 4
    assert summary_metrics(jan2)["matched_intervals"] == 0
    assert summary_metrics(jan2)["mae_mw"] is None


def test_error_histogram_counts_all_matched_errors(settings, actuals_frame, forecasts_frame):
    combined = join_actuals_and_forecasts(actuals_frame, forecasts_frame, settings)
    bins = error_histogram(combined, bin_width=500.0)
    assert sum(item["count"] for item in bins) == 4


def test_daily_accuracy_uses_delivery_date(settings, actuals_frame, forecasts_frame):
    combined = join_actuals_and_forecasts(actuals_frame, forecasts_frame, settings)
    daily = daily_accuracy(combined)
    assert daily[0]["delivery_date"] == "2026-01-01"
    assert daily[0]["matched_intervals"] == 4


def test_positive_error_is_overforecast():
    frame = pd.DataFrame(
        {
            "missing_actual": [False],
            "missing_forecast": [False],
            "forecast_generation_mw": [120.0],
            "actual_generation_mw": [100.0],
            "forecast_error_mw": [20.0],
            "delivery_date": ["2026-01-01"],
            "start_time": [pd.Timestamp("2026-01-01T00:00:00Z")],
        }
    )
    metrics = summary_metrics(frame)
    assert metrics["mean_forecast_error_mw"] > 0
