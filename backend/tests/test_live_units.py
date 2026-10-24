from app.analysis.service import load_analysis_bundle


def test_cached_or_demo_generation_is_mw():
    settings, intervals, metadata = load_analysis_bundle()
    assert settings.generation_unit == "MW"
    valid = intervals.loc[~intervals["missing_actual"] & ~intervals["missing_forecast"]]
    if valid.empty:
        return
    assert valid["actual_generation_mw"].max() < 100000
    assert valid["forecast_generation_mw"].max() < 100000
    assert metadata.get("source") in {"elexon", "demonstration"}
